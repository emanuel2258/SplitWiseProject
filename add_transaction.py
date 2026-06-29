#!/usr/bin/env python3
"""
Module for adding individual transactions to Splitwise.
Provides functionality to add single expenses without requiring a CSV file.
"""

from typing import Dict, Any, Optional
from datetime import datetime
from src.utils.logger import get_logger
from src.utils.config_loader import get_card_cashback
from src.utils.date_utils import parse_expense_date


logger = get_logger()


def prompt_transaction_details() -> Dict[str, Any]:
    """
    Interactively prompt user for transaction details.
    
    Returns:
        Dictionary containing transaction information
    """
    print("\n" + "="*60)
    print("ADD NEW TRANSACTION")
    print("="*60 + "\n")
    
    transaction = {}
    
    # Get date
    while True:
        date_input = input("Date (YYYY-MM-DD or MM/DD/YY) [today]: ").strip()
        if not date_input:
            transaction['date'] = datetime.now().strftime('%Y-%m-%d')
            break
        try:
            transaction['date'] = parse_expense_date(date_input)
            break
        except ValueError as e:
            print(f"Invalid date format: {e}. Please try again.")
    
    # Get description
    while True:
        description = input("Description: ").strip()
        if description:
            transaction['description'] = description
            break
        print("Description is required.")
    
    # Get category
    while True:
        category = input("Category (e.g., Restaurants, Groceries): ").strip()
        if category:
            transaction['category'] = category
            break
        print("Category is required.")
    
    # Get amount
    while True:
        try:
            amount = float(input("Amount ($): ").strip())
            if amount <= 0:
                print("Amount must be positive.")
                continue
            transaction['amount'] = amount
            break
        except ValueError:
            print("Invalid amount. Please enter a number.")
    
    # Get card/account
    card = input("Card name (optional, for cashback calculation): ").strip()
    if card:
        transaction['account'] = card
    
    print("\n" + "="*60 + "\n")
    
    return transaction


def calculate_transaction_amount(
    transaction: Dict[str, Any],
    config: Dict[str, Any]
) -> float:
    """
    Calculate final transaction amount after cashback.
    
    Args:
        transaction: Transaction dictionary
        config: Configuration dictionary
    
    Returns:
        Final amount after cashback deduction
    """
    original_amount = transaction['amount']
    
    # If no card specified, return original amount
    if 'account' not in transaction:
        logger.info("No card specified, using original amount (no cashback)")
        return original_amount
    
    # Calculate cashback
    cashback_rate = get_card_cashback(
        config,
        transaction['account'],
        transaction['category'],
        transaction.get('date')
    )
    
    cashback_amount = original_amount * cashback_rate
    final_amount = original_amount - cashback_amount
    
    logger.info(
        f"Cashback: {cashback_rate*100:.1f}% = ${cashback_amount:.2f}, "
        f"Final amount: ${final_amount:.2f}"
    )
    
    return round(final_amount, 2)


def format_transaction_for_expense(
    transaction: Dict[str, Any],
    config: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Format transaction into expense structure.
    
    Args:
        transaction: Raw transaction data
        config: Configuration dictionary
    
    Returns:
        Formatted expense dictionary
    """
    final_amount = calculate_transaction_amount(transaction, config)
    
    return {
        'date': transaction['date'],
        'description': transaction['description'],
        'category': transaction['category'],
        'amount': str(final_amount)
    }


def print_transaction_summary(transaction: Dict[str, Any]):
    """
    Print formatted transaction summary.
    
    Args:
        transaction: Transaction dictionary
    """
    print("\n" + "="*60)
    print("TRANSACTION SUMMARY")
    print("="*60)
    print(f"Date: {transaction['date']}")
    print(f"Description: {transaction['description']}")
    print(f"Category: {transaction['category']}")
    print(f"Amount: ${transaction['amount']}")
    if 'account' in transaction:
        print(f"Card: {transaction['account']}")
    print("="*60 + "\n")


def confirm_transaction() -> bool:
    """
    Ask user to confirm transaction before uploading.
    
    Returns:
        True if user confirms, False otherwise
    """
    while True:
        response = input("Upload this transaction to Splitwise? [Y/n]: ").strip().lower()
        
        if not response or response in ['y', 'yes']:
            return True
        elif response in ['n', 'no']:
            return False
        else:
            print("Please enter 'y' or 'n'")


def add_single_transaction(
    date: Optional[str] = None,
    description: Optional[str] = None,
    category: Optional[str] = None,
    amount: Optional[float] = None,
    account: Optional[str] = None
) -> Dict[str, Any]:
    """
    Create a transaction from command-line arguments.
    
    Args:
        date: Transaction date (YYYY-MM-DD)
        description: Transaction description
        category: Expense category
        amount: Transaction amount
        account: Card/account name
    
    Returns:
        Transaction dictionary
    
    Raises:
        ValueError: If required fields are missing
    """
    if not all([description, category, amount]):
        raise ValueError("Description, category, and amount are required")
    
    transaction = {
        'date': date or datetime.now().strftime('%Y-%m-%d'),
        'description': description,
        'category': category,
        'amount': float(amount)
    }
    
    if account:
        transaction['account'] = account
    
    return transaction


# Made with Bob

# Made with Bob
