import streamlit as st
import pandas as pd
import plotly.express as px
import os

FILE = "finance_data.csv"

st.set_page_config(page_title="Finance Master Dashboard", layout="wide")

st.title("💰 Finance Master Dashboard")

# Load data
if os.path.exists(FILE):
    df = pd.read_csv(FILE)
else:
    df = pd.DataFrame(columns=["Date","Type","Category","SubType","Person","Amount","Interest","Description"])

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

    category = st.selectbox("Category",
        ["Food","Travel","Shopping","Bills","Maintenance","Legal","EMI","Investment","Salary","Trading","Other"])

    subtype = st.text_input("Sub-Type (Axis / LIC / Post Office etc.)")
    person = st.text_input("Person (for lending/borrow)")
    desc = st.text_input("Description")

    submitted = st.form_submit_button("Add")

    if submitted:
        new = pd.DataFrame([[date,type_,category,subtype,person,amount,interest,desc]],
                           columns=df.columns)
        df = pd.concat([df,new],ignore_index=True)
        df.to_csv(FILE,index=False)
        st.success("✅ Added")

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

    # Balance
    balance = income_total + interest_income - (expense_total + emi_total + investment_total + borrow_total)

    # Alerts
    if emi_total > 60000:
        st.error("⚠️ EMI HIGH > 60k")

    if balance < 0:
        st.warning("⚠️ LOSS चल रहा है")

    # KPIs
    col1,col2,col3,col4,col5 = st.columns(5)
    col1.metric("💸 Expense", f"₹{expense_total}")
    col2.metric("🏦 EMI", f"₹{emi_total}")
    col3.metric("📈 Investment", f"₹{investment_total}")
    col4.metric("💰 Income", f"₹{income_total}")
    col5.metric("📊 Balance", f"₹{int(balance)}")

    # =====================
    # PIE CHART
    # =====================
    col1,col2 = st.columns(2)

    with col1:
        pie = px.pie(df[df["Type"].isin(["Expense","EMI","Investment"])],
                     names="Category", values="Amount",
                     title="Money Distribution")
        st.plotly_chart(pie,use_container_width=True)

    # =====================
    # MONTHLY BAR
    # =====================
    with col2:
        df["Month"] = df["Date"].dt.to_period("M").astype(str)
        monthly = df.groupby(["Month","Type"])["Amount"].sum().reset_index()

        bar = px.bar(monthly,x="Month",y="Amount",color="Type",
                     title="Monthly Flow")
        st.plotly_chart(bar,use_container_width=True)

    # =====================
    # % CHART
    # =====================
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

    # =====================
    # LENDING
    # =====================
    st.subheader("👥 Lending")
    st.dataframe(lending_df[["Person","Amount","Interest","InterestAmount"]])

    # =====================
    # BORROW
    # =====================
    st.subheader("💳 Borrow")
    st.dataframe(borrow_df[["Person","Amount","Interest","InterestAmount"]])

    # =====================
    # FULL DATA
    # =====================
    st.subheader("📋 All Data")
    st.dataframe(df)

else:
    st.info("No data yet")
