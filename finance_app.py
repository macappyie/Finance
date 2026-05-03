import streamlit as st
import pandas as pd
import plotly.express as px
import os
import requests

# =====================
# 🔐 SIMPLE LOGIN SYSTEM
# =====================
# =====================
# 🔐 LOGIN SYSTEM
# =====================
users = {
    "yogesh": "1234",
    "rahul": "1234",
    "amit": "1234"
}

def login():
    st.title("🔐 Login")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if username in users and users[username] == password:
            st.session_state["user"] = username
            st.success("Login successful")
            st.rerun()
        else:
            st.error("Invalid username or password")

# check login
if "user" not in st.session_state:
    login()
    st.stop()


# user specific file
FILE = f"{st.session_state['user']}_data.csv"

# logout button
if st.sidebar.button("Logout"):
    del st.session_state["user"]
    st.rerun()

st.set_page_config(page_title="Finance Master Dashboard", layout="wide")
st.title(f"💰 Finance Dashboard - {st.session_state['user']}")

# =====================
# 🌍 ECONOMIC DATA
# =====================
def get_economic_data():
    try:
        url = "https://api.tradingeconomics.com/indicators/country/india?c=guest:guest"
        res = requests.get(url, timeout=5)
        data = res.json()

        repo = None
        inflation = None
        gdp = None

        for item in data:
            if item["Category"] == "Interest Rate":
                repo = item["LatestValue"]
            elif item["Category"] == "Inflation Rate":
                inflation = item["LatestValue"]
            elif item["Category"] == "GDP Annual Growth Rate":
                gdp = item["LatestValue"]

        return repo or 6.5, inflation or 5.1, gdp or 6.7

    except:
        return 6.5, 5.1, 6.7

# =====================
# LOAD DATA
# =====================
columns = ["Date","Type","Category","SubType","Person","Amount","Interest","Description"]

if os.path.exists(FILE):
    df = pd.read_csv(FILE)
else:
    df = pd.DataFrame(columns=columns)

# =====================
# ADD ENTRY
# =====================
st.subheader("➕ Add Entry")

with st.form("entry_form"):
    col1, col2 = st.columns(2)

    with col1:
        date = st.date_input("Date")
        type_ = st.selectbox("Type", ["Expense","Income","EMI","Investment","Lending","Borrow"])

    with col2:
        amount = st.number_input("Amount", min_value=1)
        interest = st.number_input("Interest %", min_value=0)

    # dynamic category
    default_categories = ["Food","Travel","Petrol","Shopping","Bills","Maintenance","Legal","EMI","Investment","Salary","Trading","Other"]

    existing_categories = df["Category"].dropna().unique().tolist() if not df.empty else []
    all_categories = sorted(list(set(default_categories + existing_categories)))

    category_option = st.selectbox("Category", all_categories + ["➕ Add New Category"])

    if category_option == "➕ Add New Category":
        new_category = st.text_input("Enter New Category")
        category = new_category if new_category else "Other"
    else:
        category = category_option

    subtype = st.text_input("Sub-Type")
    person = st.text_input("Person")
    desc = st.text_input("Description")

    submitted = st.form_submit_button("Add")

    if submitted:
        new = pd.DataFrame([{
            "Date": date,
            "Type": type_,
            "Category": category,
            "SubType": subtype,
            "Person": person,
            "Amount": amount,
            "Interest": interest,
            "Description": desc
        }])

        df = pd.concat([df,new],ignore_index=True)
        df.to_csv(FILE,index=False)
        st.success("✅ Added")

# =====================
# ECONOMIC DATA
# =====================
st.subheader("🌍 Live Economic Data")

repo, inflation, gdp = get_economic_data()

c1,c2,c3 = st.columns(3)
c1.metric("Repo Rate", f"{repo}%")
c2.metric("Inflation", f"{inflation}%")
c3.metric("GDP", f"{gdp}%")

# =====================
# DASHBOARD
# =====================
st.subheader("📊 Dashboard")

if not df.empty:
    df["Date"] = pd.to_datetime(df["Date"])

    expense = df[df["Type"]=="Expense"]["Amount"].sum()
    emi = df[df["Type"]=="EMI"]["Amount"].sum()
    invest = df[df["Type"]=="Investment"]["Amount"].sum()
    income = df[df["Type"]=="Income"]["Amount"].sum()

    balance = income - (expense + emi + invest)

    st.metric("Balance", f"₹{int(balance)}")

    st.subheader("📋 All Data")
    st.dataframe(df)

    # delete
    st.subheader("🗑️ Delete Entry")
    idx = st.selectbox("Select row", df.index)

    if st.button("Delete"):
        df = df.drop(idx)
        df.to_csv(FILE,index=False)
        st.success("Deleted")
        st.rerun()

else:
    st.info("No data yet")

