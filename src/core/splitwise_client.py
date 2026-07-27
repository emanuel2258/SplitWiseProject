import json
import os
import time
import requests
from collections import Counter
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from src.utils.logger import get_logger
from src.utils.config_loader import get_splitwise_config
from src.utils.retention import RETENTION_DAYS


"""
Enhanced Splitwise API client with persistent count-based duplicate detection,
retry logic with exponential backoff, and dry run mode support.
"""


logger = get_logger()

_DEFAULT_LOG_PATH = 'uploaded_log.json'
_MAX_RETRIES = 3
_RETRY_BACKOFF = [1, 2, 4]  # seconds between attempts


class SplitwiseClient:
    """Client for interacting with Splitwise API."""

    def __init__(
        self,
        api_key: str,
        config: Dict[str, Any],
        dry_run: bool = False,
        log_path: str = _DEFAULT_LOG_PATH
    ):
        """
        Initialize Splitwise client.

        Args:
            api_key:  Splitwise API key
            config:   Configuration dictionary
            dry_run:  If True, don't send any requests to the API
            log_path: Path to the persistent upload log JSON file
        """
        self.api_key = api_key
        self.config = config
        self.dry_run = dry_run
        self.log_path = log_path
        self.splitwise_config = get_splitwise_config(config)
        self.base_url = 'https://secure.splitwise.com/api/v3.0'

        self.uploaded_expenses: Counter = self._load_upload_log()

        if dry_run:
            logger.info("Splitwise client initialized in DRY RUN mode - no expenses will be uploaded")
        else:
            logger.info(
                f"Splitwise client initialized "
                f"({len(self.uploaded_expenses)} previously uploaded expenses in log)"
            )

    # ------------------------------------------------------------------
    # Persistent upload log
    # ------------------------------------------------------------------

    @staticmethod
    def _key_is_expired(key: str, cutoff_date) -> bool:
        """A key is expired if its embedded date is older than cutoff_date.
        Keys with an unparseable date prefix are kept (fail safe)."""
        date_part = key.split('|', 1)[0]
        try:
            return datetime.strptime(date_part, '%Y-%m-%d').date() < cutoff_date
        except ValueError:
            return False

    def _load_upload_log(self) -> Counter:
        """Load previously uploaded expense keys from disk as occurrence counts,
        dropping entries older than RETENTION_DAYS so the log doesn't grow unbounded.

        The log is stored as a flat list of keys where a key appears once per
        actual upload, so occurrence counts survive a plain JSON round-trip."""
        if not os.path.exists(self.log_path):
            return Counter()
        try:
            with open(self.log_path, 'r') as f:
                data = json.load(f)
            counts = Counter(data.get('uploaded', []))
        except (json.JSONDecodeError, KeyError, OSError) as e:
            logger.warning(f"Could not read upload log '{self.log_path}': {e}. Starting fresh.")
            return Counter()

        cutoff_date = (datetime.now() - timedelta(days=RETENTION_DAYS)).date()
        pruned = Counter({
            key: count for key, count in counts.items()
            if not self._key_is_expired(key, cutoff_date)
        })

        removed = sum(counts.values()) - sum(pruned.values())
        if removed:
            logger.info(f"Pruned {removed} upload log entries older than {RETENTION_DAYS} days")
            try:
                with open(self.log_path, 'w') as f:
                    json.dump({'uploaded': sorted(pruned.elements())}, f, indent=2)
            except OSError as e:
                logger.warning(f"Could not persist pruned upload log '{self.log_path}': {e}")

        return pruned

    def _save_upload_log(self):
        """Persist the current occurrence counts to disk as a flat list of keys
        (one entry per upload), so counts survive a plain JSON round-trip."""
        try:
            with open(self.log_path, 'w') as f:
                json.dump({'uploaded': sorted(self.uploaded_expenses.elements())}, f, indent=2)
        except OSError as e:
            logger.error(f"Could not save upload log '{self.log_path}': {e}")

    # ------------------------------------------------------------------
    # Duplicate detection
    # ------------------------------------------------------------------

    @staticmethod
    def _expense_key(expense: Dict[str, Any]) -> str:
        return f"{expense['date']}|{expense['description']}|{expense['amount']}"

    def is_duplicate(self, expense: Dict[str, Any]) -> bool:
        """Return True if this expense has been uploaded at least once before,
        according to the persistent log."""
        key = self._expense_key(expense)
        if self.uploaded_expenses[key] > 0:
            logger.warning(f"Duplicate expense detected: {expense['description']} (${expense['amount']})")
            return True
        return False

    def mark_as_uploaded(self, expense: Dict[str, Any]):
        """Record one more occurrence of this expense as uploaded and save the log to disk."""
        self.uploaded_expenses[self._expense_key(expense)] += 1
        self._save_upload_log()

    # ------------------------------------------------------------------
    # API formatting
    # ------------------------------------------------------------------

    def format_expense_for_splitwise_group(
        self,
        expense: Dict[str, Any],
        group_id: str
    ) -> Dict[str, Any]:
        """
        Format expense data for the Splitwise API.

        Args:
            expense:  Expense dictionary
            group_id: Splitwise group ID

        Returns:
            Formatted expense body for API request
        """
        return {
            "cost": expense['amount'],
            "description": expense['description'],
            "details": self.splitwise_config.get('details_suffix', "Generated using Emanuel's Script"),
            "date": expense['date'],
            "repeat_interval": "never",
            "currency_code": self.splitwise_config.get('currency_code', 'USD'),
            "category_id": self.splitwise_config.get('default_category_id', 18),
            "group_id": group_id,
            "split_equally": self.splitwise_config.get('split_equally', True)
        }

    # ------------------------------------------------------------------
    # API request with retry
    # ------------------------------------------------------------------

    def send_expense(self, splitwise_expense: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Send a single expense to the Splitwise API.

        Retries up to 3 times with exponential backoff (1s, 2s, 4s) on
        transient network errors and timeouts. Client errors (4xx) are not
        retried since they indicate a data or auth problem.

        Args:
            splitwise_expense: Formatted expense data

        Returns:
            Response JSON if successful, None otherwise
        """
        if self.dry_run:
            logger.info(
                f"[DRY RUN] Would upload: {splitwise_expense['description']} "
                f"(${splitwise_expense['cost']}) on {splitwise_expense['date']}"
            )
            return {"dry_run": True, "success": True}

        headers = {
            'Authorization': f"Bearer {self.api_key}",
            'Accept': '*/*'
        }
        url = f'{self.base_url}/create_expense'

        for attempt in range(1, _MAX_RETRIES + 1):
            try:
                resp = requests.post(url, headers=headers, data=splitwise_expense, timeout=30)

                # Client errors (bad auth, validation) — don't retry
                if 400 <= resp.status_code < 500:
                    logger.error(
                        f"Client error {resp.status_code} for "
                        f"'{splitwise_expense['description']}': {resp.text}"
                    )
                    return None

                resp.raise_for_status()
                response_json = resp.json()

                if 'expenses' not in response_json or len(response_json['expenses']) == 0:
                    logger.error(
                        f"Failed to create expense '{splitwise_expense['description']}': "
                        f"{response_json.get('errors', 'Unknown error')}"
                    )
                    return None

                logger.info(
                    f"Successfully uploaded: {splitwise_expense['description']} "
                    f"(${splitwise_expense['cost']})"
                )
                return response_json

            except requests.exceptions.Timeout:
                logger.warning(
                    f"Timeout on attempt {attempt}/{_MAX_RETRIES} "
                    f"for '{splitwise_expense['description']}'"
                )
            except requests.exceptions.RequestException as e:
                logger.warning(
                    f"Network error on attempt {attempt}/{_MAX_RETRIES} "
                    f"for '{splitwise_expense['description']}': {e}"
                )

            if attempt < _MAX_RETRIES:
                sleep_secs = _RETRY_BACKOFF[attempt - 1]
                logger.info(f"Retrying in {sleep_secs}s...")
                time.sleep(sleep_secs)

        logger.error(
            f"All {_MAX_RETRIES} attempts failed for '{splitwise_expense['description']}'"
        )
        return None

    # ------------------------------------------------------------------
    # Batch upload
    # ------------------------------------------------------------------

    def upload_expenses(
        self,
        expenses: list,
        group_id: str,
        skip_duplicates: bool = True
    ) -> Dict[str, int]:
        """
        Upload multiple expenses to Splitwise.

        Duplicate detection is occurrence-aware: if a given date/description/amount
        combination was uploaded N times before, only the first N occurrences of that
        same combination in this batch are treated as duplicates. Any further identical
        occurrences are genuinely new expenses (e.g. two separate same-day coffees) and
        get uploaded normally.

        Args:
            expenses:        List of expense dictionaries
            group_id:        Splitwise group ID
            skip_duplicates: If True, skip expenses already in the upload log

        Returns:
            Dictionary with upload statistics
        """
        stats = {'total': len(expenses), 'uploaded': 0, 'skipped': 0, 'failed': 0}

        # Snapshot persisted counts so uploads made earlier in this same batch
        # don't shift the duplicate threshold for later occurrences of the same key.
        previously_uploaded = Counter(self.uploaded_expenses)
        seen_in_batch = Counter()

        for expense in expenses:
            key = self._expense_key(expense)
            occurrence_index = seen_in_batch[key]
            seen_in_batch[key] += 1

            if skip_duplicates and occurrence_index < previously_uploaded[key]:
                logger.warning(f"Duplicate expense detected: {expense['description']} (${expense['amount']})")
                stats['skipped'] += 1
                continue

            splitwise_expense = self.format_expense_for_splitwise_group(expense, group_id)
            response = self.send_expense(splitwise_expense)

            if response:
                stats['uploaded'] += 1
                if not self.dry_run:
                    self.mark_as_uploaded(expense)
            else:
                stats['failed'] += 1

        prefix = '[DRY RUN] ' if self.dry_run else ''
        logger.info(
            f"{prefix}Upload complete: {stats['uploaded']} uploaded, "
            f"{stats['skipped']} skipped, {stats['failed']} failed"
        )

        return stats
