import os
import expenses
import splitwise

# Script to get your expenses from CSV file, upload to splitwise and generate CSV file with the modified expenses
# The file path is relative to the current working directory of the Python script.
# When you open a file in Python using a relative file path (as opposed to an absolute file path)
# Python looks for the file in the current working directory.
if __name__ == '__main__':
    csv_read_file = f"{os.environ['CSV_READ_PATH']}{os.environ['CSV_READ_FILE_NAME']}"
    expenses_list = expenses.filter_and_calculate_expenses_from_csv(csv_read_file)
    csv_write_file = f"{os.environ['CSV_READ_PATH']}Modified_{os.environ['CSV_READ_FILE_NAME']}"
    expenses.generate_expense_csv(expenses_list, csv_write_file)

    for expense in expenses_list:
        splitwise_expense = splitwise.format_expense_for_splitwise_group(expense, os.environ['SPLITWISE_GROUP_ID'])
        splitwise.send_splitwise_expense_request(splitwise_expense)
