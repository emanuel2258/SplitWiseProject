import requests
import os


# Method to generate the body I will send to splitwise
# I got the body format here https://dev.splitwise.com/#tag/expenses/paths/~1create_expense/post
def format_expense_for_splitwise_group(expense, group_id):
    body = {
        "cost": expense['amount'],
        "description": expense['description'],
        "details": "Generated using Emanuel's Script",
        "date": expense['date'],
        "repeat_interval": "never",
        "currency_code": "USD",
        "category_id": 18,  # 18 means general expense
        "group_id": group_id,
        "split_equally": True
    }
    return body


# Method to send the expense to splitwise
def send_splitwise_expense_request(splitwise_expense):
    request_header = {
        'Authorization': f'Bearer {os.environ["SPLITWISE_API_KEY"]}',
        'Accept': '*/*'
    }
    url = 'https://secure.splitwise.com/api/v3.0/create_expense'
    try:
        resp = requests.post(url, headers=request_header, data=splitwise_expense)
        resp.raise_for_status()
    except Exception as e:
        print(f'ERROR: Failed to send the information to splitwise: {e}')
        return None
    print(
        f"Was able to send request to create expense {splitwise_expense['description']} with amount {splitwise_expense['cost']}")
    return resp
