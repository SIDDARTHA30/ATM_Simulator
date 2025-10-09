import streamlit as st
from database import conn, c

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

# -------------------------
# Streamlit Session State
# -------------------------
if "user" not in st.session_state:
    st.session_state.user = None
if "attempts" not in st.session_state:
    st.session_state.attempts = 0

st.title("🏦 ATM Simulator")

# -------------------------
# Registration / Login Menu
# -------------------------
menu = ["Register", "Login"]
choice = st.sidebar.selectbox("Menu", menu)

# -------------------------
# Registration
# -------------------------
if choice == "Register":
    st.subheader("Create New Account")
    name = st.text_input("Name")
    pin = st.text_input("4-digit PIN", type="password")
    if st.button("Register"):
        if len(pin) == 4 and pin.isdigit():
            create_user(name, pin)
            st.success("Account created! Initial balance ₹1000")
        else:
            st.error("PIN must be 4 digits")

# -------------------------
# Login
# -------------------------
elif choice == "Login":
    st.subheader("Login")
    
    # Show login form only if not already logged in
    if st.session_state.user is None:
        name = st.text_input("Name", key="login_name")
        pin = st.text_input("PIN", type="password", key="login_pin")
        if st.button("Login"):
            user = get_user(name, pin)
            if user:
                st.session_state.user = user
                st.success(f"Welcome {user['name']}!")
            else:
                st.session_state.attempts += 1
                remaining = 3 - st.session_state.attempts
                st.error(f"Invalid credentials. {remaining} attempts left.")
                if st.session_state.attempts >= 3:
                    st.warning("Card Blocked. Please contact bank.")
    # Show ATM menu after login
    if st.session_state.user is not None:
        user = st.session_state.user
        st.subheader(f"Welcome {user['name']}")
        st.write(f"Balance: ₹{user['balance']}")
        
        option = st.selectbox("Choose Option", ["Check Balance", "Deposit Money", "Withdraw Money", "Exit"])
        
        # Check Balance
        if option == "Check Balance":
            st.info(f"Your Balance: ₹{user['balance']}")
        
        # Deposit
        elif option == "Deposit Money":
            amt = st.number_input("Amount to Deposit", min_value=1)
            if st.button("Deposit"):
                if amt > 50000:
                    st.error("Deposit limit exceeded. Max ₹50,000")
                else:
                    new_balance = user['balance'] + amt
                    update_balance(user['id'], new_balance)
                    add_transaction(user['id'], "Deposit", amt)
                    st.session_state.user['balance'] = new_balance
                    st.success(f"Deposited ₹{amt}. New Balance ₹{new_balance}")
        
        # Withdraw
        elif option == "Withdraw Money":
            amt = st.number_input("Amount to Withdraw", min_value=1)
            if st.button("Withdraw"):
                if amt > 20000:
                    st.error("Withdraw limit ₹20,000")
                elif amt % 100 != 0:
                    st.error("Amount must be multiple of 100")
                elif amt > user['balance'] - 1000:
                    st.error("Insufficient funds or minimum ₹1000 required")
                else:
                    new_balance = user['balance'] - amt
                    update_balance(user['id'], new_balance)
                    add_transaction(user['id'], "Withdraw", amt)
                    st.session_state.user['balance'] = new_balance
                    st.success(f"Withdrawn ₹{amt}. New Balance ₹{new_balance}")
        
        # Exit
        elif option == "Exit":
            st.warning("Thank you for banking with us!")
            st.session_state.user = None
            st.session_state.attempts = 0
