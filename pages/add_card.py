
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from database import add_card, get_all_cards, delete_card, update_card_details
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
        background-color: rgba(248, 249, 250, 0.1);
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 10px;
        border-left: 3px solid #1f77b4;
        color: inherit;
    }
    .card-text {
        color: inherit !important;
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
            <span class="card-text"><strong>{card[1]}</strong></span><br>
            <span class="card-text">Due Date: {card[5]}</span><br>
            <span class="card-text">Limit: ${card[8]:,.2f}</span><br>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("🗑️ Delete Card", key=f"delete_{card[0]}", help="Remove this card permanently"):
            delete_card(card[0])
            st.success(f"Card '{card[1]}' deleted successfully!")
            st.rerun()
        st.markdown("<hr style='margin: 10px 0; opacity: 0.3'>", unsafe_allow_html=True)
else:
    st.info("No cards added yet.")

# Add update card details section
st.markdown("---")
st.subheader("Update Card Details")

cards = get_all_cards()
if cards:
    # Create DataFrame with necessary columns but hide ID in display
    df = pd.DataFrame(cards, columns=[
        'ID', 'Nickname', 'Statement Day', 'Payment Days After',
        'Statement Date', 'Due Date', 'Payment Status', 'Due Amount',
        'Credit Limit', 'Remarks', 'Created At'
    ])
    # Note: We keep ID column for internal use but don't display it
    
    selected_card = st.selectbox("Select Card to Update", df['Nickname'])
    if selected_card:
        card_idx = df[df['Nickname'] == selected_card].index[0]
        card_id = df.loc[card_idx, 'ID']

        with st.form(f"update_details_{card_id}"):
            new_limit = st.number_input(
                "Credit Limit",
                min_value=0.0,
                value=float(df.loc[card_idx, 'Credit Limit']),
                step=1000.0
            )
            new_remarks = st.text_area(
                "Remarks",
                value=df.loc[card_idx, 'Remarks'] if pd.notna(df.loc[card_idx, 'Remarks']) else ""
            )

            if st.form_submit_button("Update Details"):
                update_card_details(card_id, new_limit, new_remarks)
                st.success("Card details updated successfully!")
                st.experimental_rerun()
else:
    st.info("No cards available to update.")

st.markdown("""
### Tips:
- Enter a memorable nickname for your card
- Statement date is when your billing cycle ends
- Due date is when your payment is due
- Credit limit helps track your available credit
- Use remarks to note any special features or reminders
""")
