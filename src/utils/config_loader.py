import json
import os
from datetime import datetime, date as date_type
from typing import Dict, Any, List, Optional
from src.utils.logger import get_logger


"""
Configuration loader module for managing application settings.
Loads configuration from JSON file and validates environment variables.
"""


logger = get_logger()


def load_config(config_path='config.json') -> Dict[str, Any]:
    """
    Load configuration from JSON file.

    Args:
        config_path: Path to configuration file

    Returns:
        Dictionary containing configuration data

    Raises:
        FileNotFoundError: If config file doesn't exist
        json.JSONDecodeError: If config file is invalid JSON
    """
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
        logger.info(f"Configuration loaded from {config_path}")
        return config
    except FileNotFoundError:
        logger.error(f"Configuration file not found: {config_path}")
        raise
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in configuration file: {e}")
        raise


def validate_env_variables(required_vars: List[str]) -> Dict[str, str]:
    """
    Validate that all required environment variables are set.

    Args:
        required_vars: List of required environment variable names

    Returns:
        Dictionary of environment variable names and values

    Raises:
        EnvironmentError: If any required variables are missing
    """
    missing_vars = []
    env_values = {}

    for var in required_vars:
        value = os.environ.get(var)
        if not value:
            missing_vars.append(var)
        else:
            env_values[var] = value

    if missing_vars:
        error_msg = (
            f"Missing required environment variables: {', '.join(missing_vars)}\n"
            f"Please set these variables or create a .env file based on .env.example"
        )
        logger.error(error_msg)
        raise EnvironmentError(error_msg)

    logger.info("All required environment variables validated")
    return env_values


def _check_single_rate(rate_dict: Dict[str, Any], check_date: date_type) -> Optional[float]:
    """
    Validate a single date-bounded rate dict against a given date.

    Args:
        rate_dict: Dict with 'rate' and optional 'valid_from'/'valid_until' (YYYY-MM-DD)
        check_date: Date to validate against

    Returns:
        The rate if valid for check_date, None if outside the date range
    """
    rate = rate_dict.get('rate')
    if rate is None:
        return None

    valid_from = rate_dict.get('valid_from')
    valid_until = rate_dict.get('valid_until')

    if valid_from:
        try:
            if check_date < datetime.strptime(valid_from, '%Y-%m-%d').date():
                return None
        except ValueError:
            logger.warning(f"Invalid valid_from format: '{valid_from}'")

    if valid_until:
        try:
            if check_date > datetime.strptime(valid_until, '%Y-%m-%d').date():
                return None
        except ValueError:
            logger.warning(f"Invalid valid_until format: '{valid_until}'")

    return float(rate)


def _resolve_date_bounded_rate(rate_entry: Any, check_date: date_type) -> Optional[float]:
    """
    Resolve a rate entry to a float, respecting optional date bounds.

    Supported formats:
        - float/int         → always valid
        - {"rate": float, "valid_from": "YYYY-MM-DD", "valid_until": "YYYY-MM-DD"}
        - list of the above → first matching entry wins

    Args:
        rate_entry: Rate value in any of the supported formats
        check_date: The expense date to check validity against

    Returns:
        The applicable rate, or None if no valid rate found for check_date
    """
    if isinstance(rate_entry, (int, float)):
        return float(rate_entry)

    if isinstance(rate_entry, dict):
        return _check_single_rate(rate_entry, check_date)

    if isinstance(rate_entry, list):
        for entry in rate_entry:
            rate = _check_single_rate(entry, check_date)
            if rate is not None:
                return rate

    return None


def get_card_cashback(
    config: Dict[str, Any],
    account: str,
    category: str,
    expense_date: Optional[str] = None
) -> float:
    """
    Get cashback rate for a specific card and category.

    Resolves card aliases first, then looks up the rate. Rates can be plain
    floats (always valid) or date-bounded dicts/lists for rotating categories.
    Falls back to default_cashback when no valid rate is found for the date.

    Args:
        config: Configuration dictionary
        account: Card account name (full CSV value or alias)
        category: Expense category
        expense_date: Date of expense in YYYY-MM-DD format (defaults to today)

    Returns:
        Cashback rate as decimal (e.g., 0.03 for 3%)
    """
    if expense_date:
        try:
            check_date = datetime.strptime(expense_date, '%Y-%m-%d').date()
        except ValueError:
            logger.warning(f"Invalid expense_date '{expense_date}', using today for cashback lookup")
            check_date = date_type.today()
    else:
        check_date = date_type.today()

    # Resolve full CSV account name to alias
    card_aliases = config.get('card_aliases', {})
    alias = card_aliases.get(account, account)

    cards = config.get('cards', {})
    if alias not in cards:
        logger.warning(f"Card '{account}' not found in configuration. Using default 1% cashback.")
        return 0.01

    card_config = cards[alias]
    categories = card_config.get('categories', {})
    default_cashback = card_config.get('default_cashback', 0.01)

    # Wildcard rate applies to all categories (e.g. amazon_card, citi_double_cash)
    if '*' in categories:
        rate = _resolve_date_bounded_rate(categories['*'], check_date)
        if rate is not None:
            return rate

    # Category-specific rate
    if category in categories:
        rate = _resolve_date_bounded_rate(categories[category], check_date)
        if rate is not None:
            return rate
        logger.warning(
            f"No valid cashback rate for '{category}' on '{alias}' on {check_date}. "
            f"Falling back to {default_cashback*100:.0f}%. "
            f"Update config.json with current quarter's rotating categories."
        )

    return default_cashback


def get_excluded_categories(config: Dict[str, Any]) -> List[str]:
    """
    Get list of expense categories to exclude from processing.

    Args:
        config: Configuration dictionary

    Returns:
        List of category names to exclude
    """
    return config.get('excluded_categories', [])


def get_splitwise_config(config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Get Splitwise-specific configuration.

    Args:
        config: Configuration dictionary

    Returns:
        Dictionary with Splitwise settings
    """
    return config.get('splitwise', {
        'default_category_id': 18,
        'currency_code': 'USD',
        'split_equally': True,
        'details_suffix': "Generated using Emanuel's Script"
    })
