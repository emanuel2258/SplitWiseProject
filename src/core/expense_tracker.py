import csv
import json
import os
from typing import List, Dict, Any, Tuple
from src.utils.logger import get_logger
from src.utils.config_loader import get_card_cashback, get_excluded_categories
from src.utils.date_utils import parse_expense_date


"""
Enhanced expense tracking module with improved error handling,
logging, and summary reporting capabilities.
"""


logger = get_logger()


class ExpenseStats:
    """Track statistics about processed expenses."""
    
    def __init__(self):
        self.total_expenses = 0
        self.processed_expenses = 0
        self.skipped_expenses = 0
        self.failed_expenses = 0
        self.total_amount = 0.0
        self.total_cashback = 0.0
        self.category_totals = {}
        self.errors = []
    
    def add_processed(self, amount: float, cashback: float, category: str):
        """Record a successfully processed expense."""
        self.processed_expenses += 1
        self.total_amount += amount
        self.total_cashback += cashback
        
        if category not in self.category_totals:
            self.category_totals[category] = 0.0
        self.category_totals[category] += amount
    
    def add_skipped(self, reason: str):
        """Record a skipped expense."""
        self.skipped_expenses += 1
        logger.debug(f"Expense skipped: {reason}")
    
    def add_failed(self, error: str):
        """Record a failed expense."""
        self.failed_expenses += 1
        self.errors.append(error)
        logger.error(f"Expense failed: {error}")
    
    def get_summary(self) -> Dict[str, Any]:
        """Get summary statistics."""
        return {
            'total_expenses': self.total_expenses,
            'processed': self.processed_expenses,
            'skipped': self.skipped_expenses,
            'failed': self.failed_expenses,
            'total_amount': round(self.total_amount, 2),
            'total_cashback': round(self.total_cashback, 2),
            'net_amount': round(self.total_amount - self.total_cashback, 2),
            'category_breakdown': {k: round(v, 2) for k, v in self.category_totals.items()},
            'errors': self.errors
        }


def filter_and_calculate_expenses_from_csv(
    file_path: str, 
    config: Dict[str, Any]
) -> Tuple[List[Dict[str, Any]], ExpenseStats]:
    """
    Process expenses from CSV file with improved error handling and statistics.
    
    Args:
        file_path: Path to CSV file
        config: Configuration dictionary
    
    Returns:
        Tuple of (expenses list, statistics object)
    """
    expenses = []
    stats = ExpenseStats()
    excluded_categories = set(get_excluded_categories(config))
    
    try:
        with open(file_path, 'r') as csv_file:
            csv_reader = csv.DictReader(csv_file)
            
            # Check if file has content
            first_row = None
            try:
                first_row = next(csv_reader)
            except StopIteration:
                logger.warning("CSV file is empty")
                return expenses, stats
            
            # Process first row
            stats.total_expenses += 1
            if expense_should_count_check(first_row, excluded_categories):
                process_expense_row(first_row, expenses, stats, config)
            else:
                stats.add_skipped(f"Category '{first_row.get('Category')}' excluded or invalid amount")
            
            # Process remaining rows
            for row in csv_reader:
                stats.total_expenses += 1
                if expense_should_count_check(row, excluded_categories):
                    process_expense_row(row, expenses, stats, config)
                else:
                    stats.add_skipped(f"Category '{row.get('Category')}' excluded or invalid amount")
                    
    except FileNotFoundError:
        error_msg = f"CSV file not found: {file_path}"
        logger.error(error_msg)
        stats.add_failed(error_msg)
        return expenses, stats
    except Exception as e:
        error_msg = f"Error reading CSV file: {str(e)}"
        logger.error(error_msg)
        stats.add_failed(error_msg)
        return expenses, stats
    
    logger.info(f"Processed {stats.processed_expenses} expenses from {file_path}")
    return expenses, stats


def process_expense_row(
    row: Dict[str, str], 
    expenses: List[Dict[str, Any]], 
    stats: ExpenseStats,
    config: Dict[str, Any]
):
    """
    Process a single expense row.
    
    Args:
        row: CSV row data
        expenses: List to append processed expense to
        stats: Statistics tracker
        config: Configuration dictionary
    """
    try:
        original_amount = abs(float(row['Amount']))
        raw_date = row.get('Date')
        try:
            parsed_date = parse_expense_date(raw_date) if raw_date else None
        except ValueError:
            parsed_date = None
        cashback_rate = get_card_cashback(config, row['Account'], row['Category'], parsed_date)
        cashback_amount = original_amount * cashback_rate
        final_amount = original_amount - cashback_amount
        
        row['Amount'] = str(round(final_amount, 2))
        expense_info = format_and_get_expense_info(row)
        expenses.append(expense_info)
        
        stats.add_processed(final_amount, cashback_amount, row['Category'])
        
    except (ValueError, KeyError) as e:
        error_msg = f"Invalid expense data in row: {str(e)}"
        stats.add_failed(error_msg)
        logger.warning(f"Skipping row due to error: {row}")


def expense_should_count_check(expense: Dict[str, str], excluded_categories: set) -> bool:
    """
    Check if expense should be processed.
    
    Args:
        expense: Expense data dictionary
        excluded_categories: Set of categories to exclude
    
    Returns:
        True if expense should be processed, False otherwise
    """
    try:
        category = expense.get('Category', '')
        amount = float(expense.get('Amount', 0))
        
        # Only process negative amounts (expenses, not income)
        # and categories not in exclusion list
        return category not in excluded_categories and amount < 0
    except (ValueError, TypeError):
        return False


def format_and_get_expense_info(expense: Dict[str, str]) -> Dict[str, Any]:
    """
    Format expense data into standardized structure.

    Args:
        expense: Raw expense data

    Returns:
        Formatted expense dictionary

    Raises:
        ValueError: If required fields are missing or invalid
    """
    raw_date = expense.get('Date', '')
    try:
        date = parse_expense_date(raw_date)
    except ValueError:
        logger.warning(f"Could not parse date '{raw_date}', using original value")
        date = raw_date

    description = expense.get('Description', '').strip()
    category = expense.get('Category', '').strip()
    amount = expense.get('Amount', '').strip()

    if not all([date, description, category, amount]):
        raise ValueError("Missing required expense information")

    return {
        'date': date,
        'description': description,
        'category': category,
        'amount': amount
    }


def generate_expense_csv(expenses: List[Dict[str, Any]], file_path: str) -> bool:
    """
    Generate CSV file with processed expenses.
    
    Args:
        expenses: List of expense dictionaries
        file_path: Output file path
    
    Returns:
        True if successful, False otherwise
    """
    try:
        if not expenses:
            logger.warning("No expenses to write to CSV")
            return False
        
        with open(file_path, 'w', newline='') as csvfile:
            fieldnames = ['Date', 'Description', 'Category', 'Amount']
            csv_writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            csv_writer.writeheader()
            
            for expense in expenses:
                csv_writer.writerow({
                    'Date': expense['date'],
                    'Description': expense['description'],
                    'Category': expense['category'],
                    'Amount': expense['amount']
                })
        
        logger.info(f"Successfully wrote {len(expenses)} expenses to {file_path}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to write CSV file: {str(e)}")
        return False


def print_summary_report(stats: ExpenseStats):
    """
    Print formatted summary report to console.
    
    Args:
        stats: Statistics object
    """
    summary = stats.get_summary()
    
    print("\n" + "="*60)
    print("EXPENSE PROCESSING SUMMARY")
    print("="*60)
    print(f"Total expenses in file: {summary['total_expenses']}")
    print(f"Processed: {summary['processed']}")
    print(f"Skipped: {summary['skipped']}")
    print(f"Failed: {summary['failed']}")
    print(f"\nTotal amount: ${summary['total_amount']:.2f}")
    print(f"Total cashback: ${summary['total_cashback']:.2f}")
    print(f"Net amount: ${summary['net_amount']:.2f}")
    
    if summary['category_breakdown']:
        print(f"\nCategory Breakdown:")
        for category, amount in sorted(summary['category_breakdown'].items(), 
                                      key=lambda x: x[1], reverse=True):
            print(f"  {category}: ${amount:.2f}")
    
    if summary['errors']:
        print(f"\nErrors encountered:")
        for error in summary['errors']:
            print(f"  - {error}")
    
    print("="*60 + "\n")


def save_summary_json(stats: ExpenseStats, file_path: str):
    """
    Save summary statistics to JSON file.
    
    Args:
        stats: Statistics object
        file_path: Output file path
    """
    try:
        # Ensure the directory exists
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        summary = stats.get_summary()
        with open(file_path, 'w') as f:
            json.dump(summary, f, indent=2)
        logger.info(f"Summary saved to {file_path}")
    except Exception as e:
        logger.error(f"Failed to save summary JSON: {str(e)}")

# Made with Bob
