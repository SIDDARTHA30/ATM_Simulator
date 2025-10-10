import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import random

# -------------------------
# Database Setup
# -------------------------
conn = sqlite3.connect("atm.db", check_same_thread=False)
c = conn.cursor()

c.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    pin TEXT,
    balance REAL
)
''')

c.execute('''
CREATE TABLE IF NOT EXISTS transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    type TEXT,
    amount REAL,
    date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
''')
conn.commit()

# -------------------------
# Helper Functions
# -------------------------
def get_user(name, pin):
    c.execute("SELECT * FROM users WHERE name=? AND pin=?", (name, pin))
    row = c.fetchone()
    if row:
        return {"id": row[0], "name": row[1], "pin": row[2], "balance": row[3]}
    return None

def create_user(name, pin):
    c.execute("INSERT INTO users (name, pin, balance) VALUES (?, ?, ?)", (name, pin, 1000))
    conn.commit()

def update_balance(user_id, new_balance):
    c.execute("UPDATE users SET balance=? WHERE id=?", (new_balance, user_id))
    conn.commit()

def add_transaction(user_id, type_, amount):
    c.execute("INSERT INTO transactions (user_id, type, amount) VALUES (?, ?, ?)", (user_id, type_, amount))
    conn.commit()

def get_transactions(user_id):
    c.execute("SELECT type, amount, date FROM transactions WHERE user_id=? ORDER BY date DESC", (user_id,))
    return c.fetchall()

def get_all_users():
    c.execute("SELECT * FROM users")
    return c.fetchall()

def get_all_transactions():
    c.execute("SELECT * FROM transactions ORDER BY date DESC")
    return c.fetchall()

# -------------------------
# Session State
# -------------------------
if "user" not in st.session_state:
    st.session_state.user = None
if "attempts" not in st.session_state:
    st.session_state.attempts = 0

st.set_page_config(page_title="ATM Simulator", layout="wide", page_icon="🏦")
st.markdown(
    """
    <style>
    .stButton>button {height:3em;width:100%;}
    .card {padding:20px;border-radius:15px;background:#f5f5f5;text-align:center;}
    </style>
    """, unsafe_allow_html=True
)
st.title("🏦 ATM Simulator")

# -------------------------
# Sidebar
# -------------------------
st.sidebar.title("ATM Menu")
menu = ["Register", "Login", "Admin View"]
choice = st.sidebar.selectbox("Select Action", menu)

# -------------------------
# Registration
# -------------------------
if choice == "Register":
    st.subheader("📝 Create New Account")
    name = st.text_input("Name")
    pin = st.text_input("4-digit PIN", type="password")
    if st.button("Register"):
        if len(pin) == 4 and pin.isdigit():
            create_user(name, pin)
            st.success("✅ Account created! Initial balance ₹1000")
        else:
            st.error("❌ PIN must be 4 digits")

# -------------------------
# Login
# -------------------------
elif choice == "Login":
    st.subheader("🔑 Login")
    if st.session_state.user is None:
        name = st.text_input("Name", key="login_name")
        pin = st.text_input("PIN", type="password", key="login_pin")
        if st.button("Login"):
            user = get_user(name, pin)
            if user:
                st.session_state.user = user
                st.success(f"Welcome {user['name']}! 🎉")
            else:
                st.session_state.attempts += 1
                remaining = 3 - st.session_state.attempts
                st.error(f"Invalid credentials. {remaining} attempts left.")
                if st.session_state.attempts >= 3:
                    st.warning("Card Blocked. Please contact bank.")
    
    if st.session_state.user:
        user = st.session_state.user
        
        # -------------------------
        # Dashboard Cards
        # -------------------------
        st.markdown("### 💳 Account Dashboard")
        col1, col2, col3 = st.columns(3)
        col1.metric("💰 Balance", f"₹{user['balance']}")
        col2.button("💵 Deposit Money", key="deposit_button")
        col3.button("💸 Withdraw Money", key="withdraw_button")
        
        # -------------------------
        # ATM Options as Buttons
        # -------------------------
        st.markdown("### 🔹 ATM Options")
        options_col1, options_col2, options_col3 = st.columns(3)
        
        if options_col1.button("💰 Check Balance"):
            st.info(f"💰 Your Balance: ₹{user['balance']}")
        
        if options_col2.button("💵 Deposit"):
            amt = st.number_input("💵 Amount to Deposit", min_value=1, key="deposit_amt")
            if st.button("Confirm Deposit"):
                if amt > 50000:
                    st.error("❌ Deposit limit exceeded. Max ₹50,000")
                else:
                    new_balance = user['balance'] + amt
                    update_balance(user['id'], new_balance)
                    add_transaction(user['id'], "Deposit", amt)
                    st.session_state.user['balance'] = new_balance
                    st.balloons()
                    st.success(f"✅ Deposited ₹{amt}. New Balance ₹{new_balance}")
        
        if options_col3.button("💸 Withdraw"):
            amt = st.number_input("💸 Amount to Withdraw", min_value=1, key="withdraw_amt")
            if st.button("Confirm Withdraw"):
                if amt > 20000:
                    st.error("❌ Withdraw limit ₹20,000")
                elif amt % 100 != 0:
                    st.error("❌ Amount must be multiple of 100")
                elif amt > user['balance'] - 1000:
                    st.error("❌ Insufficient funds or minimum ₹1000 required")
                else:
                    new_balance = user['balance'] - amt
                    update_balance(user['id'], new_balance)
                    add_transaction(user['id'], "Withdraw", amt)
                    st.session_state.user['balance'] = new_balance
                    st.balloons()
                    st.success(f"✅ Withdrawn ₹{amt}. New Balance ₹{new_balance}")
        
        if st.button("🧾 Transaction History"):
            transactions = get_transactions(user['id'])
            if transactions:
                df = pd.DataFrame(transactions, columns=["Type", "Amount", "Date"])
                st.bar_chart(df.groupby("Type")["Amount"].sum())
                st.table(df.style.applymap(lambda x: 'color: green' if x=="Deposit" else 'color: red', subset=['Type']))
            else:
                st.info("ℹ️ No transactions yet.")
        
        if st.button("🚪 Exit"):
            st.warning("👋 Thank you for banking with us!")
            st.session_state.user = None
            st.session_state.attempts = 0

# -------------------------
# Admin View
# -------------------------
elif choice == "Admin View":
    st.subheader("🛠️ Admin Dashboard")
    st.info("View all users and transactions stored in the database.")
    
    tabs = st.tabs(["Users", "Transactions"])
    
    with tabs[0]:
        st.markdown("### 👥 Users Table")
        users = get_all_users()
        if users:
            df_users = pd.DataFrame(users, columns=["ID", "Name", "PIN", "Balance"])
            search = st.text_input("🔎 Search User by Name")
            if search:
                df_users = df_users[df_users['Name'].str.contains(search, case=False)]
            st.dataframe(df_users)
        else:
            st.info("ℹ️ No users yet.")
    
    with tabs[1]:
        st.markdown("### 💳 Transactions Table")
        transactions = get_all_transactions()
        if transactions:
            df_trans = pd.DataFrame(transactions, columns=["ID", "User ID", "Type", "Amount", "Date"])
            filter_type = st.selectbox("Filter by Type", ["All", "Deposit", "Withdraw"])
            if filter_type != "All":
                df_trans = df_trans[df_trans['Type'] == filter_type]
            st.dataframe(df_trans)
        else:
            st.info("ℹ️ No transactions yet.")
