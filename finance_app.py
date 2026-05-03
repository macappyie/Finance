import streamlit as st
import pandas as pd
import plotly.express as px
import os
import requests
from datetime import datetime

FILE = "finance_data.csv"

st.set_page_config(page_title="Finance Master Dashboard", layout="wide")

st.title("💰 Finance Master Dashboard")

# =====================
# 🌍 LIVE ECONOMIC DATA
# =====================
def get_economic_data():
    try:
        url = "https://api.tradingeconomics.com/indicators/country/india?c=guest:guest"
        res = requests.get(url, timeout=5)
        data = res.json()

        repo = inflation = gdp = None

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

    default_categories = ["Food","Travel","Petrol","Shopping","Bills","Maintenance","Legal","EMI","Investment","Salary","Trading","Business","Other"]

    if not df.empty:
        existing_categories = df["Category"].dropna().unique().tolist()
    else:
        existing_categories = []

    all_categories = list(set(default_categories + existing_categories))
    all_categories.sort()

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
st.subheader("🌍 Live Economic Data (India)")
repo, inflation, gdp = get_economic_data()

c1,c2,c3 = st.columns(3)
c1.metric("Repo Rate", f"{repo}%")
c2.metric("Inflation", f"{inflation}%")
c3.metric("GDP Growth", f"{gdp}%")

# =====================
# DASHBOARD
# =====================
st.subheader("📊 Dashboard")

if not df.empty:

    df["Date"] = pd.to_datetime(df["Date"])

    # =====================
    # FILTERS
    # =====================
    st.subheader("🔍 Filters")

    col1, col2 = st.columns(2)
    start_date = col1.date_input("Start Date", df["Date"].min())
    end_date = col2.date_input("End Date", df["Date"].max())

    category_filter = st.multiselect(
        "Category",
        options=df["Category"].unique(),
        default=df["Category"].unique()
    )

    filtered_df = df[
        (df["Date"] >= pd.to_datetime(start_date)) &
        (df["Date"] <= pd.to_datetime(end_date)) &
        (df["Category"].isin(category_filter))
    ]

    # =====================
    # MONTH CALCULATIONS
    # =====================
    today = datetime.today()

    current_month_df = df[
        (df["Date"].dt.month == today.month) &
        (df["Date"].dt.year == today.year)
    ]

    last_month = today.month - 1 if today.month > 1 else 12
    year = today.year if today.month > 1 else today.year - 1

    last_month_df = df[
        (df["Date"].dt.month == last_month) &
        (df["Date"].dt.year == year)
    ]

    current_month_expense = current_month_df[current_month_df["Type"]=="Expense"]["Amount"].sum()
    last_month_expense = last_month_df[last_month_df["Type"]=="Expense"]["Amount"].sum()

    m1, m2 = st.columns(2)
    m1.metric("📅 Current Month Expense", f"₹{int(current_month_expense)}")
    m2.metric("📅 Last Month Expense", f"₹{int(last_month_expense)}")

    # =====================
    # MAIN METRICS
    # =====================
    expense_total = filtered_df[filtered_df["Type"]=="Expense"]["Amount"].sum()
    income_total = filtered_df[filtered_df["Type"]=="Income"]["Amount"].sum()
    emi_total = filtered_df[filtered_df["Type"]=="EMI"]["Amount"].sum()
    investment_total = filtered_df[filtered_df["Type"]=="Investment"]["Amount"].sum()

    balance = income_total - (expense_total + emi_total + investment_total)

    c1,c2,c3,c4,c5 = st.columns(5)
    c1.metric("Expense", f"₹{int(expense_total)}")
    c2.metric("Income", f"₹{int(income_total)}")
    c3.metric("EMI", f"₹{int(emi_total)}")
    c4.metric("Investment", f"₹{int(investment_total)}")
    c5.metric("Balance", f"₹{int(balance)}")

    # =====================
    # LIFETIME VIEW
    # =====================
    st.subheader("📅 50 Years / Lifetime Analysis")

    df["Year"] = df["Date"].dt.year
    years = sorted(df["Year"].unique())

    selected_year = st.selectbox("Select Year", ["All Time"] + list(years))

    if selected_year == "All Time":
        year_df = df.copy()
    else:
        year_df = df[df["Year"] == selected_year]

    total_expense_all = df[df["Type"]=="Expense"]["Amount"].sum()
    st.metric("💸 Total Lifetime Expense", f"₹{int(total_expense_all)}")

    # =====================
    # YEARLY CHART
    # =====================
    yearly = df[df["Type"]=="Expense"].groupby("Year")["Amount"].sum().reset_index()
    fig1 = px.bar(yearly, x="Year", y="Amount", title="Yearly Expense")
    st.plotly_chart(fig1, use_container_width=True)

    # =====================
    # MONTHLY
    # =====================
    year_df["Month"] = year_df["Date"].dt.to_period("M").astype(str)
    monthly = year_df.groupby("Month")["Amount"].sum().reset_index()

    fig2 = px.bar(monthly, x="Month", y="Amount", title="Monthly Flow")
    st.plotly_chart(fig2, use_container_width=True)

    # =====================
    # CATEGORY
    # =====================
    cat = year_df[year_df["Type"]=="Expense"].groupby("Category")["Amount"].sum().reset_index()
    fig3 = px.pie(cat, names="Category", values="Amount", title="Category Expense")
    st.plotly_chart(fig3, use_container_width=True)

    # =====================
    # DAILY TREND
    # =====================
    daily = filtered_df.groupby(filtered_df["Date"].dt.date)["Amount"].sum().reset_index()
    fig4 = px.line(daily, x="Date", y="Amount", title="Daily Spending")
    st.plotly_chart(fig4, use_container_width=True)

    # =====================
    # DATA TABLE
    # =====================
    st.subheader("📋 Full Data")
    st.dataframe(df.sort_values(by="Date", ascending=False), height=400)

else:
    st.info("No data yet")

