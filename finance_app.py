import streamlit as st
import pandas as pd
import plotly.express as px
import os
from datetime import datetime

FILE = "finance_data.csv"

st.set_page_config(page_title="Finance Dashboard", layout="wide")
st.title("💰 Finance Master Dashboard")

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

    # 🔥 CATEGORY DROPDOWN + NEW
    default_categories = ["Food","Travel","Petrol","Shopping","Bills","Maintenance","Legal","EMI","Investment","Salary","Trading","Business","Other"]

    if not df.empty:
        existing_categories = df["Category"].dropna().unique().tolist()
    else:
        existing_categories = []

    all_categories = list(set(default_categories + existing_categories))
    all_categories.sort()

    category_option = st.selectbox("Category", all_categories + ["➕ Add New Category"])

    if category_option == "➕ Add New Category":
        category = st.text_input("Enter New Category")
    else:
        category = category_option

    subtype = st.text_input("Sub-Type")
    person = st.text_input("Person")
    desc = st.text_input("Description")

    submitted = st.form_submit_button("Add")

    if submitted:
        if not category:
            st.error("Category required")
        else:
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
# DASHBOARD
# =====================
if not df.empty:

    df["Date"] = pd.to_datetime(df["Date"])

    st.subheader("📊 Dashboard")

    expense_total = df[df["Type"]=="Expense"]["Amount"].sum()
    income_total = df[df["Type"]=="Income"]["Amount"].sum()

    c1, c2 = st.columns(2)
    c1.metric("Expense", f"₹{int(expense_total)}")
    c2.metric("Income", f"₹{int(income_total)}")

    # =====================
    # YEARLY CHART
    # =====================
    df["Year"] = df["Date"].dt.year
    yearly = df[df["Type"]=="Expense"].groupby("Year")["Amount"].sum().reset_index()

    fig = px.bar(yearly, x="Year", y="Amount", title="Yearly Expense")
    st.plotly_chart(fig, use_container_width=True)

    # =====================
    # TABLE + EDIT + DELETE
    # =====================
    st.subheader("📋 Full Data (Edit / Delete)")

    df_display = df.sort_values(by="Date", ascending=False).reset_index()

    selected_row = st.selectbox(
        "Select Entry",
        df_display.index,
        format_func=lambda x: f"{df_display.loc[x,'Date']} | {df_display.loc[x,'Category']} | ₹{df_display.loc[x,'Amount']}"
    )

    selected_data = df_display.loc[selected_row]

    col1, col2 = st.columns(2)

    # DELETE
    with col1:
        if st.button("❌ Delete"):
            real_index = df_display.loc[selected_row, "index"]
            df = df.drop(real_index)
            df.to_csv(FILE, index=False)
            st.success("Deleted")
            st.rerun()

    # EDIT
    with col2:
        if st.button("✏️ Edit"):
            st.session_state["edit_index"] = selected_row

    # =====================
    # EDIT FORM
    # =====================
    if "edit_index" in st.session_state:

        edit_idx = st.session_state["edit_index"]
        edit_data = df_display.loc[edit_idx]

        st.subheader("✏️ Edit Entry")

        new_date = st.date_input("Date", pd.to_datetime(edit_data["Date"]))
        new_type = st.selectbox("Type", ["Expense","Income","EMI","Investment","Lending","Borrow"])
        new_category = st.text_input("Category", edit_data["Category"])
        new_amount = st.number_input("Amount", value=int(edit_data["Amount"]))

        if st.button("💾 Save Changes"):
            real_index = df_display.loc[edit_idx, "index"]

            df.loc[real_index, "Date"] = new_date
            df.loc[real_index, "Type"] = new_type
            df.loc[real_index, "Category"] = new_category
            df.loc[real_index, "Amount"] = new_amount

            df.to_csv(FILE, index=False)

            del st.session_state["edit_index"]

            st.success("Updated")
            st.rerun()

else:
    st.info("No data yet")


