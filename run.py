#!/usr/bin/env python3
import os
import sys
import logging
from datetime import datetime
from dotenv import load_dotenv
from src.utils.logger import setup_logger, get_logger
from src.utils.config_loader import load_config, validate_env_variables
from src.core.expense_tracker import (
    filter_and_calculate_expenses_from_csv,
    generate_expense_csv,
    print_summary_report,
    save_summary_json
)
from src.core.splitwise_client import SplitwiseClient
from src.utils.cli import (
    create_argument_parser,
    interactive_mode,
    validate_inputs,
    print_configuration,
    confirm_proceed
)
from add_transaction import (
    prompt_transaction_details,
    format_transaction_for_expense,
    print_transaction_summary,
    confirm_transaction,
    add_single_transaction
)


"""
Main entry point for the expense tracker application.
Provides improved CLI interface with dry-run mode, better error handling,
and comprehensive reporting.
"""


def main():
    """Main application entry point."""
    
    # Load environment variables from .env file
    load_dotenv()
    
    # Parse command-line arguments
    parser = create_argument_parser()
    args = parser.parse_args()
    
    # Set up logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logger = setup_logger(level=log_level)
    
    logger.info("="*60)
    logger.info("EXPENSE TRACKER STARTED")
    logger.info(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("="*60)
    
    try:
        # Handle interactive mode
        if args.interactive:
            interactive_inputs = interactive_mode()
            
            # Update args with interactive inputs
            for key, value in interactive_inputs.items():
                setattr(args, key, value)
        
        # Validate inputs
        if not validate_inputs(args):
            logger.error("Invalid inputs provided")
            sys.exit(1)
        
        # Load configuration early (needed for transaction mode)
        logger.info(f"Loading configuration from {args.config}")
        config = load_config(args.config)
        
        # Handle transaction mode
        if args.add_transaction or any([
            args.transaction_description,
            args.transaction_category,
            args.transaction_amount
        ]):
            return handle_transaction_mode(args, config, logger)
        
        # Set default output path if not provided (only for CSV mode)
        if not args.output:
            input_filename = os.path.basename(args.input)
            # Use CSV_WRITE_PATH from environment if available, otherwise use generated_csvs directory
            csv_write_path = os.environ.get('CSV_WRITE_PATH')
            if csv_write_path:
                # Ensure the directory exists
                os.makedirs(csv_write_path, exist_ok=True)
                args.output = os.path.join(csv_write_path, f"Modified_{input_filename}")
            else:
                # Use generated_csvs directory by default
                output_dir = 'generated_csvs'
                os.makedirs(output_dir, exist_ok=True)
                args.output = os.path.join(output_dir, f"Modified_{input_filename}")
        
        # Print configuration
        print_configuration(args)
        
        # Confirm before proceeding (unless in non-interactive mode)
        if args.interactive or sys.stdin.isatty():
            if not confirm_proceed():
                logger.info("Operation cancelled by user")
                sys.exit(0)
        
        # Validate environment variables (only if not in dry-run/summary-only mode)
        if not args.dry_run and not args.summary_only:
            required_vars = ['SPLITWISE_API_KEY', 'SPLITWISE_GROUP_ID']
            
            # Allow API key from command line
            if args.api_key:
                os.environ['SPLITWISE_API_KEY'] = args.api_key
            if args.group_id:
                os.environ['SPLITWISE_GROUP_ID'] = args.group_id
            
            env_vars = validate_env_variables(required_vars)
        
        # Process expenses from CSV
        logger.info(f"Processing expenses from {args.input}")
        expenses, stats = filter_and_calculate_expenses_from_csv(args.input, config)
        
        if not expenses:
            logger.warning("No expenses to process")
            print_summary_report(stats)
            sys.exit(0)
        
        # Generate output CSV
        logger.info(f"Generating output CSV: {args.output}")
        if generate_expense_csv(expenses, args.output):
            logger.info(f"Output CSV saved successfully")
        
        # Print summary report
        print_summary_report(stats)
        
        # Save summary JSON to summaries directory
        summaries_dir = 'summaries'
        os.makedirs(summaries_dir, exist_ok=True)
        summary_filename = os.path.join(summaries_dir, f"summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        save_summary_json(stats, summary_filename)
        
        # Upload to Splitwise (unless in dry-run or summary-only mode)
        if not args.summary_only:
            group_id = args.group_id or os.environ.get('SPLITWISE_GROUP_ID')
            api_key = args.api_key or os.environ.get('SPLITWISE_API_KEY')
            
            # In dry-run mode, use dummy credentials if not provided
            if args.dry_run:
                if not api_key:
                    api_key = "dry_run_api_key"
                if not group_id:
                    group_id = "dry_run_group_id"
            elif not api_key or not group_id:
                logger.error("API key and group ID are required for uploading")
                sys.exit(1)
            
            logger.info("Initializing Splitwise client")
            splitwise = SplitwiseClient(
                api_key=api_key,
                config=config,
                dry_run=args.dry_run
            )
            
            logger.info("Uploading expenses to Splitwise")
            upload_stats = splitwise.upload_expenses(
                expenses=expenses,
                group_id=group_id,
                skip_duplicates=args.skip_duplicates
            )
            
            # Print upload summary
            print("\n" + "="*60)
            print("SPLITWISE UPLOAD SUMMARY")
            print("="*60)
            print(f"Total expenses: {upload_stats['total']}")
            print(f"Uploaded: {upload_stats['uploaded']}")
            print(f"Skipped (duplicates): {upload_stats['skipped']}")
            print(f"Failed: {upload_stats['failed']}")
            print("="*60 + "\n")
        
        logger.info("="*60)
        logger.info("EXPENSE TRACKER COMPLETED SUCCESSFULLY")
        logger.info("="*60)
        
    except FileNotFoundError as e:
        logger.error(f"File not found: {str(e)}")
        sys.exit(1)
    except EnvironmentError as e:
        logger.error(f"Environment error: {str(e)}")
        sys.exit(1)
    except KeyboardInterrupt:
        logger.info("\nOperation cancelled by user (Ctrl+C)")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        sys.exit(1)


def handle_transaction_mode(args, config, logger):
    """
    Handle single transaction addition mode.
    
    Args:
        args: Parsed command-line arguments
        config: Configuration dictionary
        logger: Logger instance
    """
    logger.info("Running in TRANSACTION MODE")
    
    # Validate environment variables (only if not in dry-run mode)
    if not args.dry_run:
        required_vars = ['SPLITWISE_API_KEY', 'SPLITWISE_GROUP_ID']
        
        # Allow API key from command line
        if args.api_key:
            os.environ['SPLITWISE_API_KEY'] = args.api_key
        if args.group_id:
            os.environ['SPLITWISE_GROUP_ID'] = args.group_id
        
        env_vars = validate_env_variables(required_vars)
    
    # Get transaction details
    if args.add_transaction:
        # Interactive transaction entry
        transaction = prompt_transaction_details()
    else:
        # Quick add from command-line arguments
        try:
            transaction = add_single_transaction(
                date=args.transaction_date,
                description=args.transaction_description,
                category=args.transaction_category,
                amount=args.transaction_amount,
                account=args.transaction_account
            )
        except ValueError as e:
            logger.error(f"Invalid transaction data: {e}")
            sys.exit(1)
    
    # Format transaction as expense
    expense = format_transaction_for_expense(transaction, config)
    
    # Print summary
    print_transaction_summary(expense)
    
    # Confirm before uploading (unless in non-interactive mode)
    if args.add_transaction or sys.stdin.isatty():
        if not confirm_transaction():
            logger.info("Transaction cancelled by user")
            sys.exit(0)
    
    # Upload to Splitwise (unless in dry-run mode)
    if not args.dry_run:
        group_id = args.group_id or os.environ.get('SPLITWISE_GROUP_ID')
        api_key = args.api_key or os.environ.get('SPLITWISE_API_KEY')
        
        if not api_key or not group_id:
            logger.error("API key and group ID are required for uploading")
            sys.exit(1)
        
        logger.info("Initializing Splitwise client")
        splitwise = SplitwiseClient(
            api_key=api_key,
            config=config,
            dry_run=False
        )
        
        logger.info("Uploading transaction to Splitwise")
        upload_stats = splitwise.upload_expenses(
            expenses=[expense],
            group_id=group_id,
            skip_duplicates=args.skip_duplicates
        )
        
        # Print upload summary
        print("\n" + "="*60)
        print("UPLOAD SUMMARY")
        print("="*60)
        if upload_stats['uploaded'] > 0:
            print("✓ Transaction uploaded successfully!")
        elif upload_stats['skipped'] > 0:
            print("⚠ Transaction skipped (duplicate)")
        else:
            print("✗ Transaction upload failed")
        print("="*60 + "\n")
        
        if upload_stats['uploaded'] > 0:
            logger.info("Transaction uploaded successfully")
        else:
            logger.error("Failed to upload transaction")
            sys.exit(1)
    else:
        print("\n[DRY RUN] Transaction would be uploaded to Splitwise\n")
        logger.info("[DRY RUN] Transaction preview complete")
    
    logger.info("="*60)
    logger.info("TRANSACTION MODE COMPLETED SUCCESSFULLY")
    logger.info("="*60)


if __name__ == '__main__':
    main()

# Made with Bob
