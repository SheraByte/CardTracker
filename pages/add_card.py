import streamlit as st
from datetime import datetime, timedelta
import sys
import os

# Add the parent directory to path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database import add_card
from utils import validate_dates

st.title("Add New Credit Card")

with st.form("new_card_form"):
    nickname = st.text_input("Card Nickname")
    statement_date = st.date_input("Statement Date", datetime.now())

    # Calculate default due date (21 days after statement)
    default_due_date = statement_date + timedelta(days=21)
    due_date = st.date_input("Due Date", default_due_date)

    status = st.selectbox("Payment Status", ["Unpaid", "Pending", "Paid"])

    # Add credit limit and remarks fields
    credit_limit = st.number_input("Credit Limit", min_value=0.0, step=1000.0)
    remarks = st.text_area("Remarks", help="Add any notes about this card")

    submit_button = st.form_submit_button("Add Card")

    if submit_button:
        if not nickname:
            st.error("Please enter a card nickname")
        else:
            valid, message = validate_dates(
                statement_date.strftime('%Y-%m-%d'),
                due_date.strftime('%Y-%m-%d')
            )
            if valid:
                add_card(
                    nickname,
                    statement_date.strftime('%Y-%m-%d'),
                    due_date.strftime('%Y-%m-%d'),
                    status,
                    credit_limit,
                    remarks
                )
                st.success("Card added successfully!")
                st.balloons()
            else:
                st.error(message)

st.markdown("""
### Tips:
- Enter a memorable nickname for your card
- Statement date is when your billing cycle ends
- Due date is when your payment is due
- Credit limit helps track your available credit
- Use remarks to note any special features or reminders
""")
