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

        category = st.selectbox("Category", categories)

    subtype = st.text_input("Sub-Type")
    person = st.text_input("Person")
    desc = st.text_input("Description")

    submitted = st.form_submit_button("Add")

    if submitted:
        cursor.execute('''
        INSERT INTO finance
        (Date, Type, Category, SubType, Person, Amount, Interest, Description)
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
# ECONOMIC DATA
# =====================
st.subheader("🌍 Live Economic Data (India)")

repo, inflation, gdp = get_economic_data()

c1, c2, c3 = st.columns(3)
    t1.metric("💰 Trading Profit", f"₹{trading_profit:,.0f}")
    t2.metric("📉 Trading Loss", f"₹{trading_loss:,.0f}")
    t3.metric("📊 Net Trading", f"₹{net_trading:,.0f}")

    # =====================
    # CHARTS
    # =====================
    col1, col2 = st.columns(2)

    with col1:
        pie = px.pie(
            df[df["Type"].isin(["Expense", "EMI", "Investment"])],
            names="Category",
            values="Amount",
            title="Money Distribution"
        )

        st.plotly_chart(pie, use_container_width=True)

    with col2:
        df["Month"] = pd.to_datetime(df["Date"]).dt.to_period("M").astype(str)

        monthly = df.groupby(["Month", "Type"])["Amount"].sum().reset_index()

        bar = px.bar(
            monthly,
            x="Month",
            y="Amount",
            color="Type",
            title="Monthly Flow"
        )

        st.plotly_chart(bar, use_container_width=True)

    # =====================
    # DELETE ENTRY
    # =====================
    st.subheader("🗑️ Delete Entry")

    delete_id = st.selectbox("Select ID", df["id"])

    if st.button("Delete Selected Entry"):
        cursor.execute("DELETE FROM finance WHERE id=?", (int(delete_id),))
        conn.commit()

        st.success("✅ Deleted")
        st.rerun()

    # =====================
    # SHOW DATA
    # =====================
    st.subheader("📋 All Data")
    st.dataframe(df)

else:
    st.info("No data yet")
