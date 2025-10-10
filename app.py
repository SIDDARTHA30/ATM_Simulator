import streamlit as st
import sqlite3
import pandas as pd

# -------------------------
# Connect to local SQLite DB
# -------------------------
conn = sqlite3.connect("atm.db", check_same_thread=False)
c = conn.cursor()

# -------------------------
# Create tables if not exist
# -------------------------
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
if "pin_input" not in st.session_state:
    st.session_state.pin_input = ""
if "atm_action" not in st.session_state:
    st.session_state.atm_action = None
if "num_input" not in st.session_state:
    st.session_state.num_input = ""

# Initialize delete/clear flags
for k in ["pin_input", "num_input"]:
    if k + "_del" not in st.session_state:
        st.session_state[k + "_del"] = False
    if k + "_clear" not in st.session_state:
        st.session_state[k + "_clear"] = False

# -------------------------
# Page Config & Style
# -------------------------
st.set_page_config(page_title="ATM Simulator", layout="wide", page_icon="🏦")
st.markdown("""
<style>
.stButton>button {height:3em;width:100%; margin-top:5px;}
.card {padding:20px;border-radius:15px;background:#f5f5f5;text-align:center;margin-bottom:10px;}
h1, h2, h3 {color:#003366;}
</style>
""", unsafe_allow_html=True)
st.title("🏦 ATM Simulator - Realistic ATM Mode")

# -------------------------
# Sidebar Menu
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
# Numeric Keypad Helper
# -------------------------
def keypad_input(label, key):
    st.markdown(f"**{label}:** `{st.session_state[key]}`")
    cols = st.columns(3)
    for i, num in enumerate(range(1, 10)):
        if cols[i % 3].button(str(num), key=f"{key}_{num}"):
            st.session_state[key] += str(num)
    cols[0].button("0", key=f"{key}_0")
    cols[1].button("⌫", key=f"{key}_del")
    cols[2].button("Clear", key=f"{key}_clear")
    
    if st.session_state[key + "_del"]:
        st.session_state[key] = st.session_state[key][:-1]
        st.session_state[key + "_del"] = False
    if st.session_state[key + "_clear"]:
        st.session_state[key] = ""
        st.session_state[key + "_clear"] = False

# -------------------------
# Login with Keypad
# -------------------------
if choice == "Login":
    st.subheader("🔑 Login with Numeric Keypad")
    if st.session_state.user is None:
        name = st.text_input("Name", key="login_name")
        st.markdown("Enter 4-digit PIN:")
        keypad_input("PIN", "pin_input")
        if st.button("Login"):
            user = get_user(name, st.session_state.pin_input)
            if user:
                st.session_state.user = user
                st.session_state.pin_input = ""
                st.success(f"Welcome {user['name']}! 🎉")
            else:
                st.session_state.attempts += 1
                remaining = 3 - st.session_state.attempts
                st.error(f"Invalid credentials. {remaining} attempts left.")
                st.session_state.pin_input = ""
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
        
        # ATM Action Selection
        if st.session_state.atm_action is None:
            cols = st.columns(4)
            if cols[0].button("💵 Deposit"):
                st.session_state.atm_action = "Deposit"
                st.session_state.num_input = ""
            if cols[1].button("💸 Withdraw"):
                st.session_state.atm_action = "Withdraw"
                st.session_state.num_input = ""
            if cols[2].button("🧾 History"):
                st.session_state.atm_action = "History"
            if cols[3].button("🚪 Exit"):
                st.warning("👋 Thank you for banking with us!")
                st.session_state.user = None
                st.session_state.attempts = 0
                st.session_state.atm_action = None
        
        # -------------------------
        # Deposit / Withdraw via Keypad
        # -------------------------
        if st.session_state.atm_action in ["Deposit", "Withdraw"]:
            st.markdown(f"### Enter Amount to {st.session_state.atm_action}")
            keypad_input("Amount", "num_input")
            if st.button("Confirm"):
                amt = int(st.session_state.num_input) if st.session_state.num_input else 0
                if st.session_state.atm_action == "Deposit":
                    if amt > 0 and amt <= 50000:
                        new_balance = user['balance'] + amt
                        update_balance(user['id'], new_balance)
                        add_transaction(user['id'], "Deposit", amt)
                        st.session_state.user['balance'] = new_balance
                        st.balloons()
                        st.success(f"✅ Deposited ₹{amt}. New Balance ₹{new_balance}")
                        st.session_state.atm_action = None
                    else:
                        st.error("❌ Invalid deposit amount (1-50000)")
                elif st.session_state.atm_action == "Withdraw":
                    if amt > 0 and amt <= 20000 and amt % 100 == 0 and amt <= user['balance'] - 1000:
                        new_balance = user['balance'] - amt
                        update_balance(user['id'], new_balance)
                        add_transaction(user['id'], "Withdraw", amt)
                        st.session_state.user['balance'] = new_balance
                        st.balloons()
                        st.success(f"✅ Withdrawn ₹{amt}. New Balance ₹{new_balance}")
                        st.session_state.atm_action = None
                    else:
                        st.error("❌ Invalid withdraw amount or insufficient funds")
        
        # -------------------------
        # Transaction History
        # -------------------------
        if st.session_state.atm_action == "History":
            transactions = get_transactions(user['id'])
            if transactions:
                df = pd.DataFrame(transactions, columns=["Type", "Amount", "Date"])
                st.bar_chart(df.groupby("Type")["Amount"].sum())
                st.table(df.style.applymap(lambda x: 'color: green' if x=="Deposit" else 'color: red', subset=['Type']))
            else:
                st.info("ℹ️ No transactions yet.")
            st.session_state.atm_action = None

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
