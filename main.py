import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from database import init_db, get_all_cards, update_card, delete_card
from utils import validate_dates, get_status_color, format_card_data

# Initialize the database
init_db()

# Page configuration
st.set_page_config(
    page_title="Credit Card Payment Tracker",
    page_icon="💳",
    layout="wide"
)

# Custom CSS
st.markdown("""
    <style>
    .status-pill {
        padding: 5px 15px;
        border-radius: 15px;
        font-weight: bold;
        text-align: center;
    }
    .main-header {
        color: #1f77b4;
        text-align: center;
        margin-bottom: 30px;
    }
    .date-info {
        font-size: 0.9em;
        color: #666;
    }
    .amount {
        font-weight: bold;
        color: #2c3e50;
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
        default="All"
    )

with col2:
    sort_by = st.selectbox(
        "Sort by",
        ["Due Date", "Statement Date", "Created At"]
    )

# Get and display cards
cards = get_all_cards()
df = format_card_data(cards)

if not df.empty:
    # Apply filters
    if "All" not in filter_status and filter_status:
        df = df[df['Payment Status'].isin(filter_status)]

    # Apply sorting
    if sort_by == "Due Date":
        df = df.sort_values(by="Due Date")
    elif sort_by == "Statement Date":
        df = df.sort_values(by="Statement Date")
    else:
        df = df.sort_values(by="Created At")

    # Display cards
    for idx, row in df.iterrows():
        with st.container():
            st.markdown("---")
            col1, col2, col3 = st.columns([2, 2, 1])

            with col1:
                st.subheader(row['Nickname'])
                status_color = get_status_color(row['Payment Status'])
                st.markdown(
                    f"<div class='status-pill' style='background-color: {status_color}; color: white;'>"
                    f"{row['Payment Status']}</div>",
                    unsafe_allow_html=True
                )

            with col2:
                st.write("Statement Date:", row['Statement Date'])
                st.write("Due Date:", row['Due Date'])
                if row['Current Due Amount'] > 0:
                    st.markdown(f"<p class='amount'>Due Amount: ${row['Current Due Amount']:,.2f}</p>", 
                              unsafe_allow_html=True)

            with col3:
                if st.button("Update Dates & Status", key=f"edit_{row['ID']}"):
                    st.session_state['editing'] = row['ID']
                if st.button("Delete", key=f"delete_{row['ID']}"):
                    delete_card(row['ID'])
                    st.rerun()

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
                            st.rerun()
                        else:
                            st.error(message)

else:
    st.info("No credit cards added yet. Use the 'Add New Credit Card' page to add your first card!")




import streamlit as st
# Import all your modules
from database import init_db, get_all_cards, update_card, delete_card
from utils import validate_dates, get_status_color, format_card_data

# Initialize database
init_db()

# Page configuration
st.set_page_config(
    page_title="Credit Card Payment Tracker",
    page_icon="💳",
    layout="wide"
)

# Navigation
page = st.sidebar.radio("Navigation", ["Card Overview", "Add New Card", "Card Details"])

# Display the selected page
if page == "Card Overview":
    # Insert your main page code here
    # (The content of your current main.py)
    st.markdown("<h1 class='main-header'>Credit Card Payment Tracker</h1>", unsafe_allow_html=True)
    # ... rest of your main page code
    
elif page == "Add New Card":
    # Insert your add_card.py code here
    st.title("Add New Credit Card")
    # ... rest of your add_card code
    
elif page == "Card Details":
    # Insert your card_details.py code here
    st.title("Credit Card Details")
    # ... rest of your card_details code
