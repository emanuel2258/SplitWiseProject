#!/usr/bin/env python3
"""
Helper script to process monthly expense files.
Automatically finds the most recent transaction file and processes it.
"""

import os
import sys
import glob
from datetime import datetime

try:
    from dotenv import load_dotenv
except ImportError:
    print("ERROR: python-dotenv not installed. Run: pip3 install -r requirements.txt")
    sys.exit(1)


def find_latest_transaction_file(transactions_path):
    """
    Find the most recent transaction file in the directory.
    
    Args:
        transactions_path: Path to transactions directory
    
    Returns:
        Path to the most recent transaction file
    """
    pattern = os.path.join(transactions_path, "*.csv")
    files = glob.glob(pattern)
    
    if not files:
        print(f"No CSV files found in {transactions_path}")
        return None
    
    # Filter out .DS_Store and other non-transaction files
    transaction_files = [f for f in files if 'transactions.csv' in f]
    
    if not transaction_files:
        print(f"No transaction CSV files found in {transactions_path}")
        return None
    
    # Sort by modification time, most recent first
    transaction_files.sort(key=os.path.getmtime, reverse=True)
    
    return transaction_files[0]


def main():
    """Main entry point."""
    # Load environment variables from .env file
    load_dotenv()
    
    # Get paths from environment, default to transactions directory
    csv_read_path = os.environ.get('CSV_READ_PATH', 'transactions')
    csv_write_path = os.environ.get('CSV_WRITE_PATH', 'generated_csvs')
    
    # Ensure directories exist
    os.makedirs(csv_read_path, exist_ok=True)
    os.makedirs(csv_write_path, exist_ok=True)
    
    # Find latest transaction file
    print(f"Looking for transaction files in: {csv_read_path}")
    latest_file = find_latest_transaction_file(csv_read_path)
    
    if not latest_file:
        sys.exit(1)
    
    filename = os.path.basename(latest_file)
    print(f"Found latest transaction file: {filename}")
    print(f"Last modified: {datetime.fromtimestamp(os.path.getmtime(latest_file)).strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Ask user to confirm
    response = input(f"\nProcess this file? [Y/n]: ").strip().lower()
    if response and response not in ['y', 'yes']:
        print("Cancelled.")
        sys.exit(0)
    
    # Ask if dry run
    dry_run = input("Run in dry-run mode (preview only)? [Y/n]: ").strip().lower()
    dry_run_flag = "--dry-run" if not dry_run or dry_run in ['y', 'yes'] else ""
    
    # Build command
    cmd = f"python3 run.py --input \"{latest_file}\" {dry_run_flag}"
    
    print(f"\nExecuting: {cmd}\n")
    print("="*60)
    
    # Execute the command
    os.system(cmd)


if __name__ == '__main__':
    main()

# Made with Bob
