# ATM Simulator – Streamlit Web App

## Project Overview
This project is a simple ATM Simulator built using Python, Streamlit and SQLite database.  
The application allows users to create an account, login using a PIN, deposit money, withdraw money and view transaction history.

The goal of this project is to understand how real banking systems work and to practice building a full Python web application with database integration.

---

## Technologies Used
- Python
- Streamlit (Web App)
- SQLite (Database)
- Pandas

---

## Features

### User Features
- Register a new account with 4-digit PIN  
- Secure login using numeric keypad  
- View account balance  
- Deposit money  
- Withdraw money with ATM rules  
- View transaction history  

### Admin Features
- View all users stored in database  
- View all transactions  
- Filter transactions by type  

---

## ATM Rules Implemented
- New users receive ₹1000 initial balance  
- Maximum deposit limit: ₹50,000  
- Maximum withdraw limit: ₹20,000  
- Withdraw amount must be multiples of ₹100  
- Minimum balance of ₹1000 must remain in account  

---

## Database Design

Two tables are used.

Users Table:
- id
- name
- pin
- balance

Transactions Table:
- id
- user_id
- type (Deposit / Withdraw)
- amount
- date

---

## What I Learned
- Building web apps using Streamlit  
- Working with SQLite database  
- User authentication basics  
- Session management in Streamlit  
- CRUD operations (Create, Read, Update)

---

## How to Run the App
1. Install requirements  
2. Run the Streamlit app  
3. Open the browser and start using the ATM application

---

This project helped me understand full Python application development with database and user interface.
