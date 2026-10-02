import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import requests
import ollama
from datetime import datetime

API_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="FinPlanBot", layout="centered")

# ------------------------------
# Session Variables Initialization
# ------------------------------
if "step" not in st.session_state:
    st.session_state.step = 1
if "user_id" not in st.session_state:
    st.session_state.user_id = None

convo = []

def stream_response(prompt):
    convo.append({'role': 'user', 'content': prompt})
    response = ''
    stream = ollama.chat(model='llama3.2', messages=convo, stream=True)
    for chunk in stream:
        response += chunk['message']['content']
    convo.append({'role': 'assistant', 'content': response})
    return response

def go_to_next_step():
    st.session_state.step += 1

# ------------------------------
# Step 1: Welcome Page (User Info)
# ------------------------------
if st.session_state.step == 1:
    st.title("💰 Welcome to FinPlanBot!")
    st.markdown("Your Smart Personal Finance Assistant")

    name = st.text_input("Enter your Name")
    age = st.number_input("Age", min_value=10, max_value=100)
    email = st.text_input("Email (optional)")

    if st.button("Start Budgeting"):
        if name and age:
            user_data = {"name": name, "age": age, "email": email}
            res = requests.post(f"{API_URL}/add_user/", json=user_data)
            if res.status_code == 200:
                st.session_state.user_id = res.json()["user_id"]
                st.session_state.name = name
                go_to_next_step()
            else:
                st.error("⚠️ Could not save user in backend.")
        else:
            st.warning("Please enter your name and age to continue.")

# ------------------------------
# Step 2: Budget Setup
# ------------------------------
elif st.session_state.step == 2:
    st.title("💵 Let's Setup Your Budget")
    income = st.number_input("Monthly Income (₹)", min_value=0.0)

    if st.button("Save Budget & Continue"):
        if income > 0:
            budget_data = {"user_id": st.session_state.user_id, "monthly_budget": income}
            res = requests.post(f"{API_URL}/set_budget/", json=budget_data)
            if res.status_code == 200:
                st.session_state.income = income
                go_to_next_step()
            else:
                st.error("⚠️ Failed to save budget.")
        else:
            st.warning("Please enter your monthly income.")

# ------------------------------
# Step 3: Dashboard
# ------------------------------
elif st.session_state.step == 3:
    st.title(f"👋 Welcome, {st.session_state.name}")
    st.header("🤖 FinPlanBot Dashboard")

    # 💸 Expense Tracker
    st.subheader("💸 Expense Tracker")
    category_subtypes = {
        "Food": ["Groceries", "Dining Out", "Snacks"],
        "Rent": ["House Rent", "PG/Hostel", "Loan EMI"],
        "Transport": ["Fuel", "Public Transport", "Taxi"],
        "Utilities": ["Electricity", "Water Bill", "Internet", "Mobile Recharge"],
        "Entertainment": ["Streaming", "Movies", "Games"],
        "Education": ["Tuition", "Books", "Online Courses"],
        "Others": ["Medical", "Shopping", "Donations"]
    }

    with st.form("expense_form"):
        col1, col2 = st.columns(2)
        with col1:
            date = st.date_input("Date", datetime.now())
            category = st.selectbox("Category", list(category_subtypes.keys()))
        with col2:
            subtype = st.selectbox("Sub-Category", category_subtypes.get(category, []))
        amount = st.number_input("Amount (₹)", min_value=0.0, format="%.2f")
        description = st.text_input("Optional Description")

        if st.form_submit_button("Log Expense"):
            expense_data = {
                "user_id": st.session_state.user_id,
                "date": str(date),
                "category": category,
                "subcategory": subtype,
                "amount": amount,
                "description": description
            }
            res = requests.post(f"{API_URL}/add_expense/", json=expense_data)
            if res.status_code == 200:
                st.success(f"Expense of ₹{amount:.2f} saved!")
            else:
                st.error("⚠️ Failed to save expense.")

    if st.button("📥 Refresh Expenses"):
        res = requests.get(f"{API_URL}/expenses/{st.session_state.user_id}")
        if res.status_code == 200:
            expenses = pd.DataFrame(res.json()["expenses"],
                                    columns=["Date", "Category", "Sub-Category", "Amount", "Description"])
            st.dataframe(expenses)

    # 🎯 Goal Planner
    st.subheader("🎯 Goal Planner")
    with st.form("goal_form"):
        goal_name = st.text_input("Goal Name")
        target = st.number_input("Target Amount", min_value=100.0)
        months = st.slider("Timeline (months)", 1, 24, 6)
        if st.form_submit_button("Set Goal"):
            goal_data = {"user_id": st.session_state.user_id,
                         "goal_name": goal_name,
                         "target": target,
                         "months": months}
            res = requests.post(f"{API_URL}/add_goal/", json=goal_data)
            if res.status_code == 200:
                st.success(f"Goal '{goal_name}' saved!")

    if st.button("📊 View Goals"):
        res = requests.get(f"{API_URL}/goals/{st.session_state.user_id}")
        if res.status_code == 200:
            goals = pd.DataFrame(res.json()["goals"], columns=["Goal", "Target", "Months"])
            st.dataframe(goals)

    # 🔔 Budget Alerts
    if st.button("🔔 Check Budget Status"):
        res = requests.get(f"{API_URL}/check_budget/{st.session_state.user_id}")
        if res.status_code == 200:
            st.info(res.json())
