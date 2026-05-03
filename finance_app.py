import streamlit as st
import pandas as pd
import plotly.express as px
import os
import requests

FILE = "finance_data.csv"

st.set_page_config(page_title="Finance Master Dashboard", layout="wide")

st.title("💰 Finance Master Dashboard")

# =====================
# 🌍 LIVE ECONOMIC DATA FUNCTION
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

    # 🔥 UPDATED CATEGORY (Business added)
    default_categories = ["Food","Travel","Petrol","Shopping","Bills","Maintenance","Legal","EMI","Investment","Salary","Trading","Business","Poli Bhaji Kendra","Dominos","KFC","Movie","Kirana","Waste","Other"]

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

    subtype = st.text_input("Sub-Type (Axis / LIC / Post Office etc.)")
    person = st.text_input("Person (for lending/borrow)")
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
# 🌍 LIVE ECONOMIC DATA
# =====================
st.subheader("🌍 Live Economic Data (India)")

repo, inflation, gdp = get_economic_data()

colA, colB, colC = st.columns(3)
colA.metric("🏦 Repo Rate", f"{repo}%")
colB.metric("📈 Inflation", f"{inflation}%")
colC.metric("📊 GDP Growth", f"{gdp}%")

# =====================
# DASHBOARD
# =====================
st.subheader("📊 Dashboard")

if not df.empty:
    df["Date"] = pd.to_datetime(df["Date"])

    expense_total = df[df["Type"]=="Expense"]["Amount"].sum()
    emi_total = df[df["Type"]=="EMI"]["Amount"].sum()
    investment_total = df[df["Type"]=="Investment"]["Amount"].sum()
    income_total = df[df["Type"]=="Income"]["Amount"].sum()

    lending_df = df[df["Type"]=="Lending"].copy()
    lending_df["InterestAmount"] = (lending_df["Amount"]*lending_df["Interest"])/100
    interest_income = lending_df["InterestAmount"].sum()

    borrow_df = df[df["Type"]=="Borrow"].copy()
    borrow_df["InterestAmount"] = (borrow_df["Amount"]*borrow_df["Interest"])/100
    borrow_total = borrow_df["Amount"].sum()

    balance = income_total + interest_income - (expense_total + emi_total + investment_total + borrow_total)

    if emi_total > 60000:
        st.error("⚠️ EMI HIGH > 60k")

    if balance < 0:
        st.warning("⚠️ LOSS चल रहा है")

    col1,col2,col3,col4,col5 = st.columns(5)
    col1.metric("💸 Expense", f"₹{expense_total}")
    col2.metric("🏦 EMI", f"₹{emi_total}")
    col3.metric("📈 Investment", f"₹{investment_total}")
    col4.metric("💰 Income", f"₹{income_total}")
    col5.metric("📊 Balance", f"₹{int(balance)}")

    # =====================
    # 💼 BUSINESS / TRADING SUMMARY
    # =====================
    st.subheader("💼 Trading / Business Summary")

    business_income = df[
        (df["Type"]=="Income") &
        (df["Category"].isin(["Business","Trading"]))
    ]["Amount"].sum()

    business_loss = df[
        (df["Type"]=="Expense") &
        (df["Category"].isin(["Business","Trading"]))
    ]["Amount"].sum()

    net_business = business_income - business_loss

    b1, b2, b3 = st.columns(3)
    b1.metric("💰 Business Profit", f"₹{business_income}")
    b2.metric("📉 Business Loss", f"₹{business_loss}")
    b3.metric("📊 Net Business", f"₹{net_business}")

    # =====================
    # CHARTS
    # =====================
    col1,col2 = st.columns(2)

    with col1:
        pie = px.pie(df[df["Type"].isin(["Expense","EMI","Investment"])],
                     names="Category", values="Amount",
                     title="Money Distribution")
        st.plotly_chart(pie,use_container_width=True)

    with col2:
        df["Month"] = df["Date"].dt.to_period("M").astype(str)
        monthly = df.groupby(["Month","Type"])["Amount"].sum().reset_index()

        bar = px.bar(monthly,x="Month",y="Amount",color="Type",
                     title="Monthly Flow")
        st.plotly_chart(bar,use_container_width=True)

    if income_total > 0:
        expense_pct = (expense_total/income_total)*100
        emi_pct = (emi_total/income_total)*100
        invest_pct = (investment_total/income_total)*100

        pct_df = pd.DataFrame({
            "Category":["Expense","EMI","Investment"],
            "Percentage":[expense_pct,emi_pct,invest_pct]
        })

        st.subheader("📊 Income Usage %")
        pct_chart = px.bar(pct_df,x="Category",y="Percentage",text="Percentage")
        st.plotly_chart(pct_chart,use_container_width=True)

    st.subheader("👥 Lending")
    st.dataframe(lending_df[["Person","Amount","Interest","InterestAmount"]])

    st.subheader("💳 Borrow")
    st.dataframe(borrow_df[["Person","Amount","Interest","InterestAmount"]])

    # =====================
    # DELETE ENTRY
    # =====================
    st.subheader("🗑️ Delete Entry")

    delete_index = st.selectbox("Select row to delete", df.index)

    if st.button("Delete Selected Entry"):
        df = df.drop(delete_index)
        df.to_csv(FILE, index=False)
        st.success("Deleted successfully!")
        st.rerun()

    st.subheader("📋 All Data")
    st.dataframe(df)

else:
    st.info("No data yet")
