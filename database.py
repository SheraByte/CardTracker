
import sqlite3
from datetime import datetime, timedelta

def init_db():
    conn = sqlite3.connect('credit_cards.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS credit_cards
        (id INTEGER PRIMARY KEY AUTOINCREMENT,
         nickname TEXT NOT NULL,
         statement_day INTEGER NOT NULL,
         payment_days_after INTEGER NOT NULL,
         current_statement_date TEXT NOT NULL,
         current_due_date TEXT NOT NULL,
         payment_status TEXT NOT NULL,
         current_due_amount REAL DEFAULT 0,
         credit_limit REAL DEFAULT 0,
         remarks TEXT,
         created_at TEXT NOT NULL)
    ''')
    conn.commit()
    conn.close()

def add_card(nickname, statement_date, due_date, payment_status, credit_limit=0, remarks=''):
    conn = sqlite3.connect('credit_cards.db')
    c = conn.cursor()

    # Extract statement day and calculate payment days after
    statement_day = datetime.strptime(statement_date, '%Y-%m-%d').day
    due_date_obj = datetime.strptime(due_date, '%Y-%m-%d')
    statement_date_obj = datetime.strptime(statement_date, '%Y-%m-%d')
    payment_days_after = (due_date_obj - statement_date_obj).days

    c.execute('''
        INSERT INTO credit_cards 
        (nickname, statement_day, payment_days_after, 
         current_statement_date, current_due_date, payment_status,
         credit_limit, remarks, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (nickname, statement_day, payment_days_after, statement_date, 
          due_date, payment_status, credit_limit, remarks,
          datetime.now().strftime('%Y-%m-%d')))
    conn.commit()
    conn.close()

def get_all_cards():
    conn = sqlite3.connect('credit_cards.db')
    c = conn.cursor()

    # Get current date
    today = datetime.now()

    # Update dates for all cards
    c.execute('''
        SELECT id, statement_day, payment_days_after, current_statement_date
        FROM credit_cards
    ''')
    cards = c.fetchall()

    for card in cards:
        card_id, statement_day, payment_days_after, current_statement_date = card
        current_statement = datetime.strptime(current_statement_date, '%Y-%m-%d')

        # If we're past the current statement date, update to next month
        if today > current_statement:
            # Calculate next statement date
            try:
                if today.day > statement_day:
                    # Handle month overflow
                    if today.month == 12:
                        next_statement = datetime(today.year + 1, 1, statement_day)
                    else:
                        next_statement = datetime(today.year, today.month + 1, statement_day)
                else:
                    next_statement = datetime(today.year, today.month, statement_day)
            except ValueError:
                # Handle invalid dates (e.g., Feb 30)
                if today.month == 12:
                    next_statement = datetime(today.year + 1, 1, 1)
                else:
                    next_statement = datetime(today.year, today.month + 1, 1)

            # Calculate next due date
            next_due_date = next_statement + timedelta(days=payment_days_after)

            # Update the dates and reset due amount for new cycle
            c.execute('''
                UPDATE credit_cards
                SET current_statement_date = ?, current_due_date = ?, 
                    payment_status = ?, current_due_amount = ?
                WHERE id = ?
            ''', (next_statement.strftime('%Y-%m-%d'), 
                 next_due_date.strftime('%Y-%m-%d'),
                 'Unpaid', 0, card_id))

    # Commit any updates
    conn.commit()

    # Get all updated cards
    c.execute('SELECT * FROM credit_cards')
    updated_cards = c.fetchall()
    conn.close()
    return updated_cards

def update_card(card_id, nickname, statement_date, due_date, payment_status, due_amount=None):
    conn = sqlite3.connect('credit_cards.db')
    c = conn.cursor()

    # Extract statement day and calculate payment days after
    statement_day = datetime.strptime(statement_date, '%Y-%m-%d').day
    due_date_obj = datetime.strptime(due_date, '%Y-%m-%d')
    statement_date_obj = datetime.strptime(statement_date, '%Y-%m-%d')
    payment_days_after = (due_date_obj - statement_date_obj).days

    if due_amount is not None:
        c.execute('''
            UPDATE credit_cards
            SET nickname = ?, 
                statement_day = ?,
                payment_days_after = ?,
                current_statement_date = ?,
                current_due_date = ?,
                payment_status = ?,
                current_due_amount = ?
            WHERE id = ?
        ''', (nickname, statement_day, payment_days_after, statement_date, 
              due_date, payment_status, due_amount, card_id))
    else:
        c.execute('''
            UPDATE credit_cards
            SET nickname = ?, 
                statement_day = ?,
                payment_days_after = ?,
                current_statement_date = ?,
                current_due_date = ?,
                payment_status = ?
            WHERE id = ?
        ''', (nickname, statement_day, payment_days_after, statement_date, 
              due_date, payment_status, card_id))
    conn.commit()
    conn.close()

def delete_card(card_id):
    conn = sqlite3.connect('credit_cards.db')
    c = conn.cursor()
    c.execute('DELETE FROM credit_cards WHERE id = ?', (card_id,))
    conn.commit()
    conn.close()

def update_card_details(card_id, credit_limit, remarks):
    conn = sqlite3.connect('credit_cards.db')
    c = conn.cursor()
    c.execute('''
        UPDATE credit_cards
        SET credit_limit = ?,
            remarks = ?
        WHERE id = ?
    ''', (credit_limit, remarks, card_id))
    conn.commit()
    conn.close()
