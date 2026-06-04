import argparse
import sys
from typing import Optional
from src.utils.logger import get_logger


"""
Command-line interface module for the expense tracker application.
Provides interactive prompts and argument parsing.
"""


logger = get_logger()


def create_argument_parser() -> argparse.ArgumentParser:
    """
    Create and configure argument parser.
    
    Returns:
        Configured ArgumentParser instance
    """
    parser = argparse.ArgumentParser(
        description='Process expenses from CSV and upload to Splitwise',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Process expenses with dry run (preview only)
  python cli.py --input expenses.csv --dry-run
  
  # Process and upload to Splitwise (uses default group ID 9168077)
  python cli.py --input expenses.csv
  
  # Interactive mode (prompts for all inputs)
  python cli.py --interactive
  
  # Generate summary report only
  python cli.py --input expenses.csv --summary-only
  
  # Add a single transaction interactively (uses default group ID 9168077)
  python cli.py --add-transaction
  
  # Quick add a transaction via command line
  python cli.py --transaction-description "Dinner" --transaction-category "Restaurants"
               --transaction-amount 45.50
  
  # Override default group ID if needed
  python cli.py --add-transaction --group-id 12345
        """
    )
    
    parser.add_argument(
        '--input', '-i',
        type=str,
        help='Path to input CSV file containing expenses'
    )
    
    parser.add_argument(
        '--output', '-o',
        type=str,
        help='Path for output CSV file (default: Modified_<input_filename>)'
    )
    
    parser.add_argument(
        '--config', '-c',
        type=str,
        default='config.json',
        help='Path to configuration file (default: config.json)'
    )
    
    parser.add_argument(
        '--group-id', '-g',
        type=str,
        default='9168077',
        help='Splitwise group ID for uploading expenses (default: 9168077)'
    )
    
    parser.add_argument(
        '--api-key', '-k',
        type=str,
        help='Splitwise API key (can also use SPLITWISE_API_KEY env var)'
    )
    
    parser.add_argument(
        '--dry-run', '-d',
        action='store_true',
        help='Preview expenses without uploading to Splitwise'
    )
    
    parser.add_argument(
        '--summary-only', '-s',
        action='store_true',
        help='Only generate summary report, do not upload to Splitwise'
    )
    
    parser.add_argument(
        '--interactive', '-I',
        action='store_true',
        help='Run in interactive mode with prompts'
    )
    
    parser.add_argument(
        '--skip-duplicates',
        action='store_true',
        default=True,
        help='Skip duplicate expenses (default: True)'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose logging'
    )
    
    parser.add_argument(
        '--add-transaction', '-a',
        action='store_true',
        help='Add a single transaction interactively'
    )
    
    parser.add_argument(
        '--transaction-date',
        type=str,
        help='Transaction date (YYYY-MM-DD) for quick add'
    )
    
    parser.add_argument(
        '--transaction-description',
        type=str,
        help='Transaction description for quick add'
    )
    
    parser.add_argument(
        '--transaction-category',
        type=str,
        help='Transaction category for quick add'
    )
    
    parser.add_argument(
        '--transaction-amount',
        type=float,
        help='Transaction amount for quick add'
    )
    
    parser.add_argument(
        '--transaction-account',
        type=str,
        help='Card/account name for quick add (optional)'
    )
    
    return parser


def prompt_for_input(prompt_text: str, default: Optional[str] = None) -> str:
    """
    Prompt user for input with optional default value.
    
    Args:
        prompt_text: Text to display to user
        default: Default value if user presses enter
    
    Returns:
        User input or default value
    """
    if default:
        prompt_text = f"{prompt_text} [{default}]"
    
    prompt_text += ": "
    user_input = input(prompt_text).strip()
    
    if not user_input and default:
        return default
    
    return user_input


def prompt_yes_no(prompt_text: str, default: bool = False) -> bool:
    """
    Prompt user for yes/no response.
    
    Args:
        prompt_text: Text to display to user
        default: Default value if user presses enter
    
    Returns:
        True for yes, False for no
    """
    default_str = "Y/n" if default else "y/N"
    prompt_text = f"{prompt_text} [{default_str}]: "
    
    while True:
        response = input(prompt_text).strip().lower()
        
        if not response:
            return default
        
        if response in ['y', 'yes']:
            return True
        elif response in ['n', 'no']:
            return False
        else:
            print("Please enter 'y' or 'n'")


def interactive_mode() -> dict:
    """
    Run interactive mode to gather all required inputs.
    
    Returns:
        Dictionary with user inputs
    """
    print("\n" + "="*60)
    print("EXPENSE TRACKER - INTERACTIVE MODE")
    print("="*60 + "\n")
    
    inputs = {}
    
    # Get input file
    inputs['input'] = prompt_for_input(
        "Enter path to input CSV file",
        default="expenses.csv"
    )
    
    # Get output file
    default_output = f"Modified_{inputs['input'].split('/')[-1]}"
    inputs['output'] = prompt_for_input(
        "Enter path for output CSV file",
        default=default_output
    )
    
    # Get config file
    inputs['config'] = prompt_for_input(
        "Enter path to config file",
        default="config.json"
    )
    
    # Ask about dry run
    inputs['dry_run'] = prompt_yes_no(
        "Run in dry-run mode (preview only)?",
        default=True
    )
    
    if not inputs['dry_run']:
        # Get Splitwise details
        inputs['group_id'] = prompt_for_input(
            "Enter Splitwise group ID"
        )
        
        inputs['api_key'] = prompt_for_input(
            "Enter Splitwise API key (or press Enter to use env var)"
        )
        
        inputs['skip_duplicates'] = prompt_yes_no(
            "Skip duplicate expenses?",
            default=True
        )
    else:
        inputs['summary_only'] = True
    
    print("\n" + "="*60 + "\n")
    
    return inputs


def validate_inputs(args: argparse.Namespace) -> bool:
    """
    Validate command-line arguments.
    
    Args:
        args: Parsed arguments
    
    Returns:
        True if valid, False otherwise
    """
    # Transaction mode validation
    if args.add_transaction:
        # In transaction mode, input file is not required
        # Group ID now has a default value, so no need to check
        return True
    
    # Quick transaction validation
    has_transaction_args = any([
        args.transaction_description,
        args.transaction_category,
        args.transaction_amount
    ])
    
    if has_transaction_args:
        # If any transaction arg is provided, all required ones must be present
        if not all([args.transaction_description, args.transaction_category, args.transaction_amount]):
            logger.error("For quick transaction add, description, category, and amount are all required")
            return False
        # Group ID now has a default value, so no need to check
        return True
    
    # Regular CSV mode validation
    if not args.interactive and not args.input:
        logger.error("Input file is required (use --input, --interactive, or --add-transaction)")
        return False
    
    # Group ID now has a default value, so validation passes
    
    return True


def print_configuration(args: argparse.Namespace):
    """
    Print current configuration to console.
    
    Args:
        args: Parsed arguments
    """
    print("\n" + "="*60)
    print("CONFIGURATION")
    print("="*60)
    print(f"Input file: {args.input}")
    print(f"Output file: {args.output or 'Auto-generated'}")
    print(f"Config file: {args.config}")
    print(f"Dry run: {args.dry_run}")
    print(f"Summary only: {args.summary_only}")
    
    if not args.dry_run and not args.summary_only:
        print(f"Splitwise group ID: {args.group_id}")
        print(f"Skip duplicates: {args.skip_duplicates}")
    
    print("="*60 + "\n")


def confirm_proceed() -> bool:
    """
    Ask user to confirm before proceeding.
    
    Returns:
        True if user confirms, False otherwise
    """
    return prompt_yes_no("Proceed with these settings?", default=True)

# Made with Bob
