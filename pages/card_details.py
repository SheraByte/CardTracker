import streamlit as st
import pandas as pd
import sys
import os

# Add the parent directory to path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database import get_all_cards, update_card_details

st.title("Credit Card Details")

# Get all cards
cards = get_all_cards()
if cards:
    # Create DataFrame with relevant columns
    df = pd.DataFrame(cards, columns=[
        'ID', 'Nickname', 'Statement Day', 'Payment Days After',
        'Statement Date', 'Due Date', 'Payment Status', 'Due Amount',
        'Credit Limit', 'Remarks', 'Created At'
    ])

    # Display basic details in a table
    st.write("### Card Overview")
    overview_df = df[['Nickname', 'Credit Limit', 'Remarks']].copy()
    overview_df['Credit Limit'] = overview_df['Credit Limit'].apply(lambda x: f"${x:,.2f}")
    st.table(overview_df)

    # Allow editing credit limit and remarks
    st.write("### Update Card Details")
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
    st.info("No credit cards added yet. Use the 'Add New Credit Card' page to add your first card!")
