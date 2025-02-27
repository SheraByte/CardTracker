import streamlit as st
from storage import CardStorage
from datetime import datetime

# Initialize session state
if 'card_storage' not in st.session_state:
    st.session_state.card_storage = CardStorage()

def main():
    st.set_page_config(
        page_title="Credit Card Payment Tracker",
        page_icon="💳",
        layout="wide"
    )

    st.title("💳 Credit Card Payment Tracker")
    st.header("Payment Status Dashboard")

    cards_df = st.session_state.card_storage.get_all_cards()

    if len(cards_df) == 0:
        st.info("No credit cards added yet")
        return

    # Filtering
    status_filter = st.selectbox("Filter by Status", 
                              options=['All', 'Unpaid', 'Pending', 'Paid'])

    filtered_df = cards_df
    if status_filter != 'All':
        filtered_df = cards_df[cards_df['payment_status'] == status_filter]

    # Display simplified cards view
    for _, card in filtered_df.iterrows():
        with st.container():
            col1, col2 = st.columns([3, 1])

            with col1:
                st.subheader(card['nickname'])
                st.write(f"Statement Date: {card['statement_date']}")
                st.write(f"Due Date: {card['due_date']}")

            with col2:
                status_color = {
                    'Paid': 'green',
                    'Unpaid': 'red',
                    'Pending': 'orange'
                }[card['payment_status']]

                st.markdown(
                    f'<div style="padding: 10px; border-radius: 5px; '
                    f'background-color: {status_color}; color: white; '
                    f'text-align: center;">{card["payment_status"]}</div>',
                    unsafe_allow_html=True
                )

            st.markdown("<hr>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()
