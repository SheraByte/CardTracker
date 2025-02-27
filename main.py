
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from database import init_db, get_all_cards, update_card
from utils import validate_dates, get_status_color, format_card_data

# Initialize the database
init_db()

# Page configuration
st.set_page_config(
    page_title="Credit Card Payment Tracker",
    page_icon="💳",
    layout="wide"
)

# Initialize session state if not done already
if 'editing' not in st.session_state:
    st.session_state['editing'] = None

# Custom CSS with dark mode compatibility
st.markdown("""
    <style>
    .status-pill {
        padding: 5px 15px;
        border-radius: 15px;
        font-weight: bold;
        text-align: center;
        display: inline-block;
    }
    .main-header {
        color: #1f77b4;
        text-align: center;
        margin-bottom: 30px;
    }
    .date-info {
        font-size: 0.9em;
    }
    .amount {
        font-weight: bold;
    }
    .card-container {
        padding: 15px;
        border-radius: 10px;
        margin-bottom: 15px;
        border-left: 4px solid #1f77b4;
        background-color: rgba(255, 255, 255, 0.05);
    }
    .divider {
        margin: 10px 0;
        opacity: 0.2;
    }
    </style>
""", unsafe_allow_html=True)

# Header
st.markdown("<h1 class='main-header'>Credit Card Payment Tracker</h1>", unsafe_allow_html=True)

# Filters
col1, col2 = st.columns(2)
with col1:
    filter_status = st.multiselect(
        "Filter by Status",
        ["All", "Paid", "Unpaid", "Pending"],
        default=["All"]
    )

with col2:
    sort_by = st.selectbox(
        "Sort by",
        ["Due Date (Earliest)", "Due Date (Latest)", "Statement Date", "Created At"]
    )

# Get and display cards
cards = get_all_cards()
df = format_card_data(cards)

if not df.empty:
    # Apply filters - fixed the status filtering logic
    if filter_status and "All" not in filter_status:
        df = df[df['Payment Status'].isin(filter_status)]

    # Apply sorting
    if sort_by == "Due Date (Earliest)":
        df = df.sort_values(by="Due Date")
    elif sort_by == "Due Date (Latest)":
        df = df.sort_values(by="Due Date", ascending=False)
    elif sort_by == "Statement Date":
        df = df.sort_values(by="Statement Date")
    else:
        df = df.sort_values(by="Created At", ascending=False)

    # Display summary stats
    total_cards = len(df)
    paid_cards = len(df[df['Payment Status'] == 'Paid'])
    pending_cards = len(df[df['Payment Status'] == 'Pending'])
    unpaid_cards = len(df[df['Payment Status'] == 'Unpaid'])
    
    st.markdown("### Overview")
    overview_cols = st.columns(4)
    with overview_cols[0]:
        st.metric("Total Cards", total_cards)
    with overview_cols[1]:
        st.metric("Paid", paid_cards)
    with overview_cols[2]:
        st.metric("Pending", pending_cards)
    with overview_cols[3]:
        st.metric("Unpaid", unpaid_cards)
    
    st.markdown("### Your Credit Cards")
    
    # Display cards
    for idx, row in df.iterrows():
        with st.container():
            st.markdown(f"""
            <div class="card-container">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <h3>{row['Nickname']}</h3>
                    <div class="status-pill" style="background-color: {get_status_color(row['Payment Status'])}; color: white;">
                        {row['Payment Status']}
                    </div>
                </div>
                <div style="display: flex; justify-content: space-between; margin-top: 10px;">
                    <div>
                        <p class="date-info">Statement Date: {row['Statement Date']}</p>
                        <p class="date-info">Due Date: {row['Due Date']}</p>
                    </div>
                    <div>
                        <p class="amount">Credit Limit: ${float(row['Credit Limit']):,.2f}</p>
                        {f"<p class='amount'>Due Amount: ${float(row['Current Due Amount']):,.2f}</p>" if float(row['Current Due Amount']) > 0 else ""}
                    </div>
                </div>
                {f"<p>Remarks: {row['Remarks']}</p>" if pd.notna(row['Remarks']) and row['Remarks'] else ""}
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("Update Dates & Status", key=f"edit_{row['ID']}"):
                st.session_state['editing'] = row['ID']

            # Edit form
            if st.session_state.get('editing') == row['ID']:
                with st.form(f"edit_form_{row['ID']}"):
                    new_nickname = st.text_input("Card Nickname", row['Nickname'])
                    new_statement_date = st.date_input(
                        "New Statement Date",
                        datetime.strptime(row['Statement Date'], '%Y-%m-%d')
                    )
                    new_due_date = st.date_input(
                        "New Due Date",
                        datetime.strptime(row['Due Date'], '%Y-%m-%d')
                    )
                    new_status = st.selectbox(
                        "Payment Status",
                        ["Unpaid", "Pending", "Paid"],
                        index=["Unpaid", "Pending", "Paid"].index(row['Payment Status'])
                    )
                    new_due_amount = st.number_input(
                        "Due Amount ($)",
                        min_value=0.0,
                        value=float(row['Current Due Amount']),
                        step=100.0
                    )

                    col1, col2 = st.columns(2)
                    with col1:
                        save = st.form_submit_button("Save Changes")
                    with col2:
                        if st.form_submit_button("Cancel"):
                            del st.session_state['editing']
                            st.rerun()

                    if save:
                        valid, message = validate_dates(
                            new_statement_date.strftime('%Y-%m-%d'),
                            new_due_date.strftime('%Y-%m-%d')
                        )
                        if valid:
                            update_card(
                                row['ID'],
                                new_nickname,
                                new_statement_date.strftime('%Y-%m-%d'),
                                new_due_date.strftime('%Y-%m-%d'),
                                new_status,
                                new_due_amount
                            )
                            del st.session_state['editing']
                            st.success(f"Card '{new_nickname}' updated successfully!")
                            st.rerun()
                        else:
                            st.error(message)

else:
    st.info("No credit cards added yet. Use the 'Add New Credit Card' page to add your first card!")
    
    # Show a tip to help new users
    st.markdown("""
    ### Getting Started
    1. Click on "Add New Credit Card" in the sidebar
    2. Enter your card details
    3. Track payment statuses and due dates here
    """)
