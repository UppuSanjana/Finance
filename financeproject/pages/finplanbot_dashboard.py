# pages/finplanbot_dashboard.py
import streamlit as st
import requests
import pandas as pd
import matplotlib.pyplot as plt

API_URL = "http://127.0.0.1:8000"

if "user_id" not in st.session_state:
    st.error("⚠️ No user found. Please start from Home page.")
    st.stop()

user_id = st.session_state["user_id"]

st.title(f"👋 Welcome, {st.session_state.get('name', 'User')}")
st.header("🤖 FinPlanBot Dashboard")

# ------------------------------
# Expense Tracker
# ------------------------------
st.subheader("💸 Expense Tracker Agent")

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
        date = st.date_input("Date")
        category = st.selectbox("Category", list(category_subtypes.keys()))
    with col2:
        subtype = st.selectbox("Sub-Category", category_subtypes.get(category, []))

    amount = st.number_input("Amount (₹)", min_value=0.0, format="%.2f")
    description = st.text_input("Optional Description", placeholder="e.g., Paid via UPI")

    if st.form_submit_button("Log Expense"):
        expense_data = {
            "user_id": user_id,
            "date": str(date),
            "category": category,
            "subcategory": subtype,
            "amount": amount,
            "description": description
        }
        res = requests.post(f"{API_URL}/add_expense/", json=expense_data)
        if res.status_code == 200:
            st.success(f"Expense of ₹{amount:.2f} under {subtype} logged!")
        else:
            st.error("⚠️ Failed to save expense.")

# Show recent expenses
res = requests.get(f"{API_URL}/expenses/{user_id}")
if res.status_code == 200:
    expenses = res.json().get("expenses", [])
    if expenses:
        df = pd.DataFrame(expenses)
        st.markdown("**🕒 Recent Expenses**")
        st.dataframe(df, use_container_width=True)

        # Pie Chart
        summary = df.groupby("subcategory")["amount"].sum().reset_index()
        fig1, ax1 = plt.subplots()
        ax1.pie(summary["amount"], labels=summary["subcategory"], autopct='%1.1f%%', startangle=90)
        st.pyplot(fig1)

# ------------------------------
# 🧾 Report Generator Agent
# ------------------------------
# ------------------------------
# 🧾 Report Generator Agent
# ------------------------------
if st.button("🧾 Generate Report"):
    res = requests.get(f"{API_URL}/expenses/{user_id}")
    if res.status_code == 200:
        expenses = res.json().get("expenses", [])
        if expenses:
            df = pd.DataFrame(expenses)
            st.subheader("🧾 Expense Summary Report")
            st.dataframe(df)

            summary = df.groupby("subcategory")["amount"].sum().reset_index()
            fig1, ax1 = plt.subplots()
            ax1.pie(summary["amount"], labels=summary["subcategory"], autopct='%1.1f%%', startangle=90)
            ax1.set_title("Expense Breakdown")
            st.pyplot(fig1)
        else:
            st.warning("No expenses to report yet.")
    else:
        st.error("⚠️ Failed to fetch report from backend.")



# ------------------------------
# 🤖 Gemini Chatbot Agent
# ------------------------------
import google.generativeai as genai

# configure Gemini with your API key
genai.configure(api_key="AIzaSyDDMRY73oXt1sQj1cFMSOknF9_0FbqOpWM")

st.subheader("💬 Chat with FinPlanBot")

# keep chat history in session
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# chat input box at bottom
user_msg = st.chat_input("Ask me anything about your finances...")

if user_msg:
    st.session_state.chat_history.append(("You", user_msg))

    # create Gemini model
    model = genai.GenerativeModel("gemini-1.5-flash")

    # send user message
    response = model.generate_content(user_msg)

    reply = response.text
    st.session_state.chat_history.append(("FinPlanBot", reply))

# display conversation
for sender, msg in st.session_state.chat_history:
    if sender == "You":
        st.chat_message("user").markdown(msg)
    else:
        st.chat_message("assistant").markdown(msg)
