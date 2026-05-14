import streamlit as st
import pandas as pd
import plotly.express as px
import sqlite3
import requests
from datetime import datetime

# =====================
# DATABASE
# =====================
conn = sqlite3.connect("finance.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS finance (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    Date TEXT,
    Type TEXT,
    Category TEXT,
    SubType TEXT,
    Person TEXT,
    Amount REAL,
    Interest REAL,
    Description TEXT
)
''')

conn.commit()

# =====================
# STREAMLIT CONFIG
# =====================
st.set_page_config(
    page_title="Finance Master Dashboard",
    layout="wide"
)

st.title("💰 Finance Master Dashboard")

# =====================
# LIVE ECONOMIC DATA
# =====================
def get_economic_data():
    try:
        url = "https://api.tradingeconomics.com/indicators/country/india?c=guest:guest"

        res = requests.get(url, timeout=5)

        data = res.json()

        repo = 6.5
        inflation = 5.1
        gdp = 6.7

        for item in data:

            if item["Category"] == "Interest Rate":
                repo = item["LatestValue"]

            elif item["Category"] == "Inflation Rate":
                inflation = item["LatestValue"]

            elif item["Category"] == "GDP Annual Growth Rate":
                gdp = item["LatestValue"]

        return repo, inflation, gdp

    except:
        return 6.5, 5.1, 6.7


# =====================
# LOAD DATA
# =====================
def load_data():
    query = "SELECT * FROM finance ORDER BY id DESC"
    return pd.read_sql(query, conn)


# =====================
# DEFAULT TYPES/CATEGORIES
# =====================
default_types = [
    "Expense",
    "Income",
    "EMI",
    "Investment",
    "Lending",
    "Borrow",
    "Trading"
]

default_categories = [
    "Food",
    "Travel",
    "Petrol",
    "Shopping",
    "Bills",
    "Maintenance",
    "EMI",
    "Investment",
    "Salary",
    "Business",
    "Movie",
    "Kirana",
    "Borrower Person",
    "Lending Person",
    "Other"
]

# =====================
# SESSION STORAGE
# =====================
if "custom_types" not in st.session_state:
    st.session_state.custom_types = []

if "custom_categories" not in st.session_state:
    st.session_state.custom_categories = []

all_types = default_types + st.session_state.custom_types
all_categories = default_categories + st.session_state.custom_categories

# =====================
# ADD ENTRY
# =====================
st.subheader("➕ Add Entry")

# =====================
# ADD NEW TYPE
# =====================
with st.expander("➕ Add New Type"):

    new_type = st.text_input("New Type")

    if st.button("Save Type"):

        if new_type.strip() != "":

            if new_type not in st.session_state.custom_types:

                st.session_state.custom_types.append(new_type)

                st.success(f"✅ {new_type} Added")

                st.rerun()

# =====================
# ADD NEW CATEGORY
# =====================
with st.expander("➕ Add New Category"):

    new_category = st.text_input("New Category")

    if st.button("Save Category"):

        if new_category.strip() != "":

            if new_category not in st.session_state.custom_categories:

                st.session_state.custom_categories.append(new_category)

                st.success(f"✅ {new_category} Added")

                st.rerun()

# =====================
# ENTRY FORM
# =====================
with st.form("entry_form"):

    col1, col2 = st.columns(2)

    with col1:

        date = st.date_input("Date")

        type_ = st.selectbox(
            "Type",
            all_types
        )

    with col2:

        amount = st.number_input(
            "Amount",
            min_value=0.0,
            value=0.0
        )

        interest = st.number_input(
            "Interest %",
            min_value=0.0,
            value=0.0
        )

    # CATEGORY
    if type_ == "Trading":

        category = st.selectbox(
            "Category",
            ["Profit", "Loss"]
        )

    else:

        category = st.selectbox(
            "Category",
            all_categories
        )

    subtype = st.text_input("Sub-Type")

    person = st.text_input("Person")

    desc = st.text_input("Description")

    submitted = st.form_submit_button("Add")

    # =====================
    # SAVE ENTRY
    # =====================
    if submitted:

        cursor.execute('''
        INSERT INTO finance
        (
            Date,
            Type,
            Category,
            SubType,
            Person,
            Amount,
            Interest,
            Description
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            str(date),
            type_,
            category,
            subtype,
            person,
            amount,
            interest,
            desc
        ))

        conn.commit()

        st.success("✅ Added Successfully")

        st.rerun()
# =====================
# LOAD DATAFRAME
# =====================
df = load_data()

# =====================
# LIVE ECONOMIC DATA
# =====================
st.subheader("🌍 Live Economic Data (India)")

repo, inflation, gdp = get_economic_data()

c1, c2, c3 = st.columns(3)

c1.metric("🏦 Repo Rate", f"{repo}%")
c2.metric("📈 Inflation", f"{inflation}%")
c3.metric("📊 GDP Growth", f"{gdp}%")

# =====================
# DASHBOARD
# =====================
if not df.empty:

    expense_total = df[
        df["Type"] == "Expense"
    ]["Amount"].sum()

    emi_total = df[
        df["Type"] == "EMI"
    ]["Amount"].sum()

    investment_total = df[
        df["Type"] == "Investment"
    ]["Amount"].sum()

    income_total = df[
        df["Type"] == "Income"
    ]["Amount"].sum()

    balance = income_total - (
        expense_total +
        emi_total +
        investment_total
    )

    st.subheader("📊 Dashboard")

    if balance < 0:
        st.warning("⚠️ LOSS चल रहा है")

    d1, d2, d3, d4, d5 = st.columns(5)

    d1.metric("💸 Expense", f"₹{expense_total:,.0f}")
    d2.metric("🏦 EMI", f"₹{emi_total:,.0f}")
    d3.metric("📈 Investment", f"₹{investment_total:,.0f}")
    d4.metric("💰 Income", f"₹{income_total:,.0f}")
    d5.metric("📊 Balance", f"₹{balance:,.0f}")

    # =====================
    # TRADING SUMMARY
    # =====================
    st.subheader("💼 Trading Summary")

    trading_profit = df[
        (df["Type"] == "Trading") &
        (df["Category"] == "Profit")
    ]["Amount"].sum()

    trading_loss = df[
        (df["Type"] == "Trading") &
        (df["Category"] == "Loss")
    ]["Amount"].sum()

    net_trading = trading_profit - trading_loss

    t1, t2, t3 = st.columns(3)

    t1.metric(
        "💰 Trading Profit",
        f"₹{trading_profit:,.0f}"
    )

    t2.metric(
        "📉 Trading Loss",
        f"₹{trading_loss:,.0f}"
    )

    t3.metric(
        "📊 Net Trading",
        f"₹{net_trading:,.0f}"
    )

    # =====================
    # CHARTS
    # =====================
    col1, col2 = st.columns(2)

    with col1:

        pie = px.pie(
            df[
                df["Type"].isin(
                    ["Expense", "EMI", "Investment"]
                )
            ],
            names="Category",
            values="Amount",
            title="Money Distribution"
        )

        st.plotly_chart(
            pie,
            use_container_width=True
        )

    with col2:

        df["Month"] = pd.to_datetime(
            df["Date"]
        ).dt.to_period("M").astype(str)

        monthly = df.groupby(
            ["Month", "Type"]
        )["Amount"].sum().reset_index()

        bar = px.bar(
            monthly,
            x="Month",
            y="Amount",
            color="Type",
            title="Monthly Flow"
        )

        st.plotly_chart(
            bar,
            use_container_width=True
        )

    # =====================
    # DELETE ENTRY
    # =====================
    st.subheader("🗑️ Delete Entry")

    delete_id = st.selectbox(
        "Select ID",
        df["id"]
    )

    if st.button("Delete Selected Entry"):

        cursor.execute(
            "DELETE FROM finance WHERE id=?",
            (int(delete_id),)
        )

        conn.commit()

        st.success("✅ Deleted")

        st.rerun()

    # =====================
    # SHOW DATA
    # =====================
    st.subheader("📋 All Data")

    st.dataframe(
        df,
        use_container_width=True
    )

else:
    st.info("No data yet")

