
import streamlit as st
from datetime import datetime, timedelta
from database import add_card, get_all_cards, delete_card
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

# Show existing cards with delete buttons
st.markdown("---")
st.subheader("Manage Existing Cards")

# Custom CSS for the card list
st.markdown("""
<style>
    .card-container {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 10px;
        border-left: 3px solid #1f77b4;
    }
    .delete-button {
        background-color: #dc3545;
        color: white;
        border: none;
        border-radius: 5px;
        padding: 5px 10px;
    }
</style>
""", unsafe_allow_html=True)

cards = get_all_cards()
if cards:
    for card in cards:
        st.markdown(f"""
        <div class="card-container">
            <strong>{card[1]}</strong><br>
            Due Date: {card[5]}<br>
            Limit: ${card[8]:,.2f}<br>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("🗑️ Delete Card", key=f"delete_{card[0]}", help="Remove this card permanently"):
            delete_card(card[0])
            st.success(f"Card '{card[1]}' deleted successfully!")
            st.rerun()
        st.markdown("<hr style='margin: 10px 0; opacity: 0.3'>", unsafe_allow_html=True)
else:
    st.info("No cards added yet.")

st.markdown("""
### Tips:
- Enter a memorable nickname for your card
- Statement date is when your billing cycle ends
- Due date is when your payment is due
- Credit limit helps track your available credit
- Use remarks to note any special features or reminders
""")
