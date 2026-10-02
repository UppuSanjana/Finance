# home.py
import streamlit as st
import requests

API_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="Welcome to FinPlanBot", page_icon="💰")

st.title("💰 Welcome to FinPlanBot!")
st.subheader("Your Smart Personal Finance Assistant")

with st.form("user_info_form"):
    name = st.text_input("Enter your Name")
    age = st.number_input("Age", min_value=10, max_value=100, step=1)
    email = st.text_input("Email (optional)")
    submitted = st.form_submit_button("👉 Continue")

if submitted:
    if name and age:
        # Assign user_id manually (length of current users + 1)
        user_id = len(requests.get(f"{API_URL}/users/").json().get("users", [])) + 1
        user_data = {"id": user_id, "name": name, "age": age, "email": email}

        res = requests.post(f"{API_URL}/add_user/", json=user_data)
        if res.status_code == 200:
            st.session_state["user_id"] = user_id
            st.session_state["name"] = name
            st.session_state["age"] = age
            st.session_state["email"] = email
            st.success(f"Welcome, {name}! Redirecting you to set your budget...")
            st.switch_page("pages/budget_setup.py")
        else:
            st.error("⚠️ Failed to register user.")
    else:
        st.warning("Please enter both name and age.")


