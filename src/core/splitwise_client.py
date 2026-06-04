import requests
import os
from typing import Dict, Any, Optional
from src.utils.logger import get_logger
from src.utils.config_loader import get_splitwise_config


"""
Enhanced Splitwise API client with improved error handling,
duplicate detection, and dry run mode support.
"""


logger = get_logger()


class SplitwiseClient:
    """Client for interacting with Splitwise API."""
    
    def __init__(self, api_key: str, config: Dict[str, Any], dry_run: bool = False):
        """
        Initialize Splitwise client.
        
        Args:
            api_key: Splitwise API key
            config: Configuration dictionary
            dry_run: If True, don't actually send requests to API
        """
        self.api_key = api_key
        self.config = config
        self.dry_run = dry_run
        self.splitwise_config = get_splitwise_config(config)
        self.base_url = 'https://secure.splitwise.com/api/v3.0'
        self.uploaded_expenses = set()
        
        if dry_run:
            logger.info("Splitwise client initialized in DRY RUN mode - no expenses will be uploaded")
        else:
            logger.info("Splitwise client initialized")
    
    def format_expense_for_splitwise_group(
        self, 
        expense: Dict[str, Any], 
        group_id: str
    ) -> Dict[str, Any]:
        """
        Format expense data for Splitwise API.
        
        Args:
            expense: Expense dictionary
            group_id: Splitwise group ID
        
        Returns:
            Formatted expense body for API request
        """
        body = {
            "cost": expense['amount'],
            "description": expense['description'],
            "details": self.splitwise_config.get('details_suffix', 'Generated using Emanuel\'s Script'),
            "date": expense['date'],
            "repeat_interval": "never",
            "currency_code": self.splitwise_config.get('currency_code', 'USD'),
            "category_id": self.splitwise_config.get('default_category_id', 18),
            "group_id": group_id,
            "split_equally": self.splitwise_config.get('split_equally', True)
        }
        return body
    
    def is_duplicate(self, expense: Dict[str, Any]) -> bool:
        """
        Check if expense has already been uploaded in this session.
        
        Args:
            expense: Expense dictionary
        
        Returns:
            True if duplicate, False otherwise
        """
        expense_key = f"{expense['date']}|{expense['description']}|{expense['amount']}"
        
        if expense_key in self.uploaded_expenses:
            logger.warning(f"Duplicate expense detected: {expense['description']} (${expense['amount']})")
            return True
        
        return False
    
    def mark_as_uploaded(self, expense: Dict[str, Any]):
        """
        Mark expense as uploaded to prevent duplicates.
        
        Args:
            expense: Expense dictionary
        """
        expense_key = f"{expense['date']}|{expense['description']}|{expense['amount']}"
        self.uploaded_expenses.add(expense_key)
    
    def send_expense(self, splitwise_expense: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Send expense to Splitwise API.
        
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
        
        request_header = {
            'Authorization': f'Bearer {self.api_key}',
            'Accept': '*/*'
        }
        url = f'{self.base_url}/create_expense'
        
        try:
            resp = requests.post(url, headers=request_header, data=splitwise_expense, timeout=30)
            resp.raise_for_status()
            response_json = resp.json()
            
            # Validate response
            if 'expenses' not in response_json or len(response_json['expenses']) == 0:
                error_msg = response_json.get('errors', 'Unknown error')
                logger.error(
                    f"Failed to create expense '{splitwise_expense['description']}': {error_msg}"
                )
                return None
            
            logger.info(
                f"Successfully uploaded: {splitwise_expense['description']} "
                f"(${splitwise_expense['cost']})"
            )
            return response_json
            
        except requests.exceptions.Timeout:
            logger.error(
                f"Timeout while uploading expense '{splitwise_expense['description']}'"
            )
            return None
        except requests.exceptions.RequestException as e:
            logger.error(
                f"Network error uploading expense '{splitwise_expense['description']}': {str(e)}"
            )
            return None
        except Exception as e:
            logger.error(
                f"Unexpected error uploading expense '{splitwise_expense['description']}': {str(e)}"
            )
            return None
    
    def upload_expenses(
        self, 
        expenses: list, 
        group_id: str,
        skip_duplicates: bool = True
    ) -> Dict[str, int]:
        """
        Upload multiple expenses to Splitwise.
        
        Args:
            expenses: List of expense dictionaries
            group_id: Splitwise group ID
            skip_duplicates: If True, skip duplicate expenses
        
        Returns:
            Dictionary with upload statistics
        """
        stats = {
            'total': len(expenses),
            'uploaded': 0,
            'skipped': 0,
            'failed': 0
        }
        
        for expense in expenses:
            # Check for duplicates
            if skip_duplicates and self.is_duplicate(expense):
                stats['skipped'] += 1
                continue
            
            # Format and send expense
            splitwise_expense = self.format_expense_for_splitwise_group(expense, group_id)
            response = self.send_expense(splitwise_expense)
            
            if response:
                stats['uploaded'] += 1
                self.mark_as_uploaded(expense)
            else:
                stats['failed'] += 1
        
        # Log summary
        if self.dry_run:
            logger.info(
                f"[DRY RUN] Would upload {stats['uploaded']} expenses, "
                f"skip {stats['skipped']}, {stats['failed']} would fail"
            )
        else:
            logger.info(
                f"Upload complete: {stats['uploaded']} uploaded, "
                f"{stats['skipped']} skipped, {stats['failed']} failed"
            )
        
        return stats

# Made with Bob
