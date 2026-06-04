import json
import os
from typing import Dict, Any, List
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


def get_card_cashback(config: Dict[str, Any], account: str, category: str) -> float:
    """
    Get cashback rate for a specific card and category.
    
    Args:
        config: Configuration dictionary
        account: Card account name
        category: Expense category
    
    Returns:
        Cashback rate as decimal (e.g., 0.03 for 3%)
    """
    cards = config.get('cards', {})
    
    if account not in cards:
        logger.warning(
            f"Card '{account}' not found in configuration. Using default 1% cashback."
        )
        return 0.01
    
    card_config = cards[account]
    categories = card_config.get('categories', {})
    
    # Check for wildcard cashback
    if '*' in categories:
        return categories['*']
    
    # Check for specific category
    if category in categories:
        return categories[category]
    
    # Return default cashback for this card
    return card_config.get('default_cashback', 0.01)


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
        'details_suffix': 'Generated using Emanuel\'s Script'
    })

# Made with Bob
