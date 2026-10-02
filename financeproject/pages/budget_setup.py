# pages/budget_setup.py
import streamlit as st
import requests

API_URL = "http://127.0.0.1:8000"

st.title("💸 Let's Set Up Your Budget")

monthly_budget = st.number_input("Enter your Monthly Budget (₹)", min_value=0.0, format="%.2f")

if st.button("Save and Continue"):
    if "user_id" not in st.session_state:
        st.error("⚠️ User not found. Please start from Home page.")
    else:
        budget_data = {"user_id": st.session_state["user_id"], "monthly_budget": monthly_budget}
        res = requests.post(f"{API_URL}/set_budget/", json=budget_data)
        if res.status_code == 200:
            st.session_state["budget"] = monthly_budget
            st.success(f"Your budget of ₹{monthly_budget} is saved!")
            st.switch_page("pages/finplanbot_dashboard.py")
        else:
            st.error("⚠️ Failed to save budget.")


