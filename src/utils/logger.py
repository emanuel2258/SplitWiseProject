import logging
import sys
import os
from datetime import datetime


"""
Logging configuration module for the expense tracking application.
Provides centralized logging with both file and console output.
"""


def setup_logger(name='expense_tracker', log_file=None, level=logging.INFO):
    """
    Set up and configure a logger with both file and console handlers.
    
    Args:
        name: Logger name
        log_file: Optional log file path. If None, creates timestamped log file
        level: Logging level (default: INFO)
    
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Remove existing handlers to avoid duplicates
    if logger.handlers:
        logger.handlers.clear()
    
    # Create formatters
    detailed_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    simple_formatter = logging.Formatter('%(levelname)s: %(message)s')
    
    # Console handler - shows INFO and above
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(simple_formatter)
    logger.addHandler(console_handler)
    
    # File handler - logs everything
    if log_file is None:
        # Create logs directory if it doesn't exist
        log_dir = 'logs'
        os.makedirs(log_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        log_file = os.path.join(log_dir, f'expense_tracker_{timestamp}.log')
    
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(detailed_formatter)
    logger.addHandler(file_handler)
    
    return logger


def get_logger(name='expense_tracker'):
    """
    Get an existing logger or create a new one if it doesn't exist.
    
    Args:
        name: Logger name
    
    Returns:
        Logger instance
    """
    logger = logging.getLogger(name)
    if not logger.handlers:
        return setup_logger(name)
    return logger

# Made with Bob
