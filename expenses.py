import csv
from typing import List


# Method to go through the csv file that contains the expenses
# and extract a JSON list that contains the formatted expenses
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


# Method to determine the amount of the expense I should count,
# since I have cashback I subtract that based on the type of expense or type of card
def calculate_expense_amount(expense):
    cards_category_cashback = {
        "Savorone - Ending in 9209": {
            "Restaurants": .03,
            "Groceries": .03
        },
        "Customized Cash Rewards Visa Signature - Ending in 3445": {
            "Groceries": .02,
            "Online": .03
        },
        "Citi Custom Cash Card - Ending in 9673": {
            "Groceries": .05
        },
        "Discover It Card - Ending in 7693": {
            "Restaurants": .05
        },
        "Credit Card - Ending in 8642": {
            "Groceries": .05
        },
        "Credit Card - Ending in 7980": {
            "*": .05
        },
        "Citi Double Cash Card - Ending in 4252": {
            "*": .02
        }

    }
    # card_categories = cards_category_cashback[expense['Account']]
    # if "Amazon" in expense['Description']:
    #     amount = float(expense['Amount']) * .95
    # elif expense['Category'] in card_categories:
    #     cashback = card_categories[expense['Category']]
    #     amount = float(expense['Amount']) * float(1-cashback)
    # else:
    #     amount = float(expense['Amount']) * .98
    if expense['Account'] in cards_category_cashback:
        card_categories = cards_category_cashback[expense['Account']]
        if "*" in card_categories:
            cashback = card_categories['*']
        elif expense['Category'] in card_categories:
            cashback = card_categories[expense['Category']]
        else:
            cashback = .01
        amount = float(expense['Amount']) * float(1 - cashback)
    return str(abs(round(amount, 2)))


# Method to check if the expense should be included in splitwise
def expense_should_count_check(expense):
    if expense['Category'] not in {'Credit Card Payments', 'Transfers', 'Refunds & Reimbursements', 'Clothing/Shoes',
                                   'Telephone'} and float(expense['Amount']) < 0:
        return True
    return False


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

