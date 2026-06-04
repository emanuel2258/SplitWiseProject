#!/usr/bin/env python3
"""
DEPRECATED: This file is kept for backward compatibility.
Please use run.py instead for the improved version with better features.

Legacy script to get your expenses from CSV file, upload to splitwise
and generate CSV file with the modified expenses.

To migrate to the new version:
  Old: python main.py
  New: python run.py --input /path/to/expenses.csv --group-id YOUR_GROUP_ID

The new version offers:
- Dry run mode for previewing
- Better error handling
- Duplicate detection
- Summary reports
- Interactive CLI
- Easier configuration via config.json
"""

import os
import sys
import warnings

warnings.warn(
    "main.py is deprecated. Please use 'python run.py' instead. "
    "See README.md for migration instructions.",
    DeprecationWarning,
    stacklevel=2
)

import expenses
import splitwise


if __name__ == '__main__':
    print("\n" + "="*60)
    print("WARNING: You are using the deprecated main.py")
    print("Please migrate to the new run.py for better features:")
    print("  python run.py --input YOUR_FILE.csv --group-id YOUR_GROUP_ID")
    print("="*60 + "\n")
    
    try:
        csv_read_file = f"{os.environ['CSV_READ_PATH']}{os.environ['CSV_READ_FILE_NAME']}"
        expenses_list = expenses.filter_and_calculate_expenses_from_csv(csv_read_file)
        
        if not expenses_list:
            print("No expenses to process")
            sys.exit(1)
        
        csv_write_file = f"{os.environ['CSV_WRITE_PATH']}Modified_{os.environ['CSV_READ_FILE_NAME']}"
        expenses.generate_expense_csv(expenses_list, csv_write_file)
        
        for expense in expenses_list:
            splitwise_expense = splitwise.format_expense_for_splitwise_group(
                expense,
                os.environ['SPLITWISE_GROUP_ID']
            )
            splitwise.send_splitwise_expense_request(splitwise_expense)
    
    except KeyError as e:
        print(f"\nERROR: Missing environment variable: {e}")
        print("Please set all required environment variables or use run.py instead")
        sys.exit(1)
    except Exception as e:
        print(f"\nERROR: {str(e)}")
        sys.exit(1)
