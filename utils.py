
import pandas as pd
from datetime import datetime

def validate_dates(statement_date, due_date):
    try:
        statement_date = datetime.strptime(statement_date, '%Y-%m-%d')
        due_date = datetime.strptime(due_date, '%Y-%m-%d')
        if due_date < statement_date:
            return False, "Due date cannot be earlier than statement date"
        return True, ""
    except ValueError:
        return False, "Invalid date format"

def get_status_color(status):
    colors = {
        'Paid': '#28a745',  # Green
        'Unpaid': '#dc3545',  # Red
        'Pending': '#ffc107'  # Yellow
    }
    return colors.get(status, 'gray')

def format_card_data(cards):
    if not cards:
        return pd.DataFrame()

    # Create DataFrame with updated column names
    df = pd.DataFrame(cards, columns=[
        'ID', 'Nickname', 'Statement Day', 'Payment Days After',
        'Statement Date', 'Due Date', 'Payment Status', 'Current Due Amount',
        'Credit Limit', 'Remarks', 'Created At'
    ])

    # Convert dates to datetime for proper formatting
    date_columns = ['Statement Date', 'Due Date', 'Created At']
    for col in date_columns:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col]).dt.strftime('%Y-%m-%d')

    return df
