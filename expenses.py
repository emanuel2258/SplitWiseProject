import csv
from typing import List
from datetime import datetime


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
    amount = float(expense['Amount'])
    cards_category_cashback = {
        "Savor - Ending in 9209": {
            "Restaurants": .03,
            "Groceries": .03,
            "Entertainment": .03
        },
        "Customized Cash Rewards Visa Signature ( ) - Ending in 4388": {
            "Groceries": .02,
            "Online": .03
        },
        "Travel Rewards Visa Signature ( ) - Ending in 8067": {
            "Travel": .015
        },
        "Citi Custom Cash Card - Ending in 9673": {
            "Restaurants": .05
        },
        "Discover It Card - Ending in 7693": {
            "Restaurants": .05,
            "Home Improvements": .05
        },
        "Chase Freedom- Ending in 8642": {
            "Amazon": .05
        },
        "Amazon Credit Card - Ending in 7980": {
            "*": .05
        },
        "Blue Cash Everyday ( ) - Ending in 1006": {
            "Groceries": .03,
            "Online": .03,
            "Gasoline/Fuel": .03,
        },
        "Citi Double Cash Card - Ending in 1713": {
            "*": .02
        }

    }
    if expense['Account'] in cards_category_cashback:
        card_categories = cards_category_cashback[expense['Account']]
        if "*" in card_categories:
            cashback = card_categories['*']
        elif expense['Category'] in card_categories:
            cashback = card_categories[expense['Category']]
        else:
            cashback = .01
        amount = amount * float(1 - cashback)
    else:
        print("The card used for this expense did not match any that I have on file, will assume that there is no "
              "cashback. This is the amount " + expense['Amount'] + " and this is the expense's account " + expense[
                  'Account'])
    return str(abs(round(amount, 2)))


# Method to check if the expense should be included in splitwise
def expense_should_count_check(expense):
    if expense['Category'] not in {'Credit Card Payments', 'Transfers', 'Refunds & Reimbursements', 'Clothing/Shoes',
                                   'Telephone', 'Rewards', 'Charitable Giving'} and float(expense['Amount']) < 0:
        return True
    return False


# Method to generate the JSON format for the expense
def format_and_get_expense_info(expense):
    # define a method to extract necessary information from an expense
    # Parse the date string and convert to YYYY-MM-DD format
    date = None
    try:
        # Parse the input date (assuming format like MM/DD/YY with 2-digit year)
        date_obj = datetime.strptime(expense['Date'], '%m/%d/%y')
        date = date_obj.strftime('%Y-%m-%d')
    except ValueError:
        try:
            # Try alternative format (MM/DD/YYYY with 4-digit year)
            date_obj = datetime.strptime(expense['Date'], '%m/%d/%Y')
            date = date_obj.strftime('%Y-%m-%d')
        except ValueError:
            try:
                # Try if already in YYYY-MM-DD format
                date_obj = datetime.strptime(expense['Date'], '%Y-%m-%d')
                date = expense['Date']  # Already in the correct format
            except ValueError:
                # If parsing fails, attempt to extract date components
                print(f"Warning: Could not parse date '{expense['Date']}', attempting to format manually")
                # Try to handle various date formats by splitting
                parts = expense['Date'].replace('/', '-').split('-')
                if len(parts) == 3:
                    try:
                        month, day, year = int(parts[0]), int(parts[1]), int(parts[2])
                        # Handle 2-digit year
                        if year < 100:
                            # Assume 20XX for years less than 50, 19XX otherwise
                            year = 2000 + year if year < 50 else 1900 + year
                        date = f"{year:04d}-{month:02d}-{day:02d}"
                    except (ValueError, IndexError):
                        date = expense['Date']  # Use original as last resort
                else:
                    date = expense['Date']  # Use original as last resort
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
