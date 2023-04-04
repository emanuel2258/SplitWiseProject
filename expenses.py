import csv
from typing import List


# Method to go through the csv file that contains the expenses and extract a JSON list that contains the formated expenses
def filter_and_calculate_expenses_from_csv(file_path):
    expenses = []
    try:
        with open(file_path, 'r') as csv_file:
            csv_reader = csv.DictReader(csv_file)
            if csv_reader.line_num == 1:
                print("File is empty")
                return None
            for row in csv_reader:
                if expense_should_count_check(row):
                    try:
                        row['Amount'] = calculate_expense_amount(row)
                        expense_info = format_and_get_expense_info(row)
                        expenses.append(expense_info)
                    except ValueError:
                        print(f"Skipping invalid row: {row}")
                        return None
    except FileNotFoundError:
        print(f"File not found, file path {file_path}")
        return None
    return expenses


# Method to determine the amount of the expense I should count, since we have cashback I substract that based on the type of expense
def calculate_expense_amount(expense):
    if expense['Category'] in {'Restaurants'} or (
            expense['Description'] in {'Amazon'} and expense['Category'] in {'General Merchandise'}):
        amount = float(expense['Amount']) * .95
    elif expense['Category'] in {'Groceries'} and expense['Description'] not in {'Costco'}:
        amount = float(expense['Amount']) * .97
    else:
        amount = float(expense['Amount']) * .98
    return str(abs(round(amount, 2)))


# Method to check if the expense should be included in splitwise
def expense_should_count_check(expense):
    if expense['Category'] in {'Credit Card Payments', 'Transfers', 'Refunds & Reimbursements', 'Clothing/Shoes'}:
        return False
    elif expense['Description'] in {'At&t', 'Lady Janes', }:
        return False
    return True


# Method to generate the JSON format for the expense
def format_and_get_expense_info(expense):
    # define a method to extract necessary information from an expense
    date = f"{expense['Date']}T12:00:00Z"  # I need to format the date for splitwise later
    description = expense['Description']
    category = expense['Category']
    amount = expense['Amount']
    if not date or not description or not category or not amount:
        raise ValueError("Missing expense information")
    return {'date': date, 'description': description, 'category': category, 'amount': amount}


# Method generate a csv file that contains the expenses I should eventually upload to splitwise
def generate_expense_csv(expenses, file_path):
    try:
        if not expenses:
            print("Expense is empty, will not write anything to the file")
            return

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
    except FileNotFoundError:
        print(f"File not found, file path {file_path}")
