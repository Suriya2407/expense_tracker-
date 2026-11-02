import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import date, datetime

from database import (
    add_transaction,
    get_transactions,
    delete_transaction,
    save_budget,
    get_budget,
)

# -------------------------------------------------
# 1. PAGE CONFIGURATION
# -------------------------------------------------
st.set_page_config(
    page_title="FinBuddy | Your Money Companion",
    page_icon="🐷",
    layout="wide",
)

# -------------------------------------------------
# 2. PLEASANT COLOURS + STYLING
# -------------------------------------------------
st.markdown(
    """
    <style>
    :root {
        --ink: #243447;
        --muted: #667085;
        --mint: #DDF5E8;
        --lavender: #EEE8FF;
        --cream: #FFF9EE;
        --white: #FFFFFF;
        --green: #25845A;
        --purple: #7256B8;
        --border: #E4EAE7;
    }

    .stApp {
        background: linear-gradient(135deg, #F2FBF6 0%, #F8F6FF 52%, #FFF9F0 100%);
        color: var(--ink);
    }

    .block-container {
        padding-top: 1.8rem;
        padding-bottom: 3rem;
        max-width: 1450px;
    }

    h1, h2, h3 {
        color: #243447 !important;
        letter-spacing: -0.3px;
    }

    p, label, .stMarkdown {
        color: #344054;
    }

    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #E1F6EA 0%, #EEE9FF 100%);
        border-right: 1px solid #DDE8E1;
    }

    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3,
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] {
        color: #243447 !important;
    }

    [data-testid="stMetric"] {
        background: rgba(255, 255, 255, 0.92);
        padding: 20px 22px;
        border-radius: 18px;
        border: 1px solid #E1EAE5;
        box-shadow: 0 7px 22px rgba(39, 72, 56, 0.06);
    }

    [data-testid="stMetricLabel"] {
        color: #667085 !important;
        font-weight: 600;
    }

    [data-testid="stMetricValue"] {
        color: #243447 !important;
        font-weight: 750;
    }

    div[data-testid="stForm"] {
        background: rgba(255, 255, 255, 0.82);
        border: 1px solid #E1EAE5;
        border-radius: 20px;
        padding: 22px;
        box-shadow: 0 8px 24px rgba(39, 72, 56, 0.05);
    }

    div.stButton > button,
    div.stFormSubmitButton > button,
    div[data-testid="stDownloadButton"] button {
        border-radius: 12px;
        border: 0;
        background: linear-gradient(90deg, #3C9B72, #6B8DE3);
        color: white;
        font-weight: 700;
        padding: 0.55rem 1rem;
        transition: all 0.2s ease-in-out;
    }

    div.stButton > button:hover,
    div.stFormSubmitButton > button:hover,
    div[data-testid="stDownloadButton"] button:hover {
        filter: brightness(1.05);
        box-shadow: 0 5px 14px rgba(60, 155, 114, 0.20);
        border: 0;
    }

    div[data-testid="stAlert"] {
        border-radius: 14px;
    }

    div[data-testid="stDataFrame"] {
        border: 1px solid #E1EAE5;
        border-radius: 14px;
        overflow: hidden;
    }

    hr {
        border-color: #DFE8E2;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# -------------------------------------------------
# 3. SIDEBAR NAVIGATION
# -------------------------------------------------
st.sidebar.markdown("# 🐷 FinBuddy")
st.sidebar.caption("A little more joy in your money journey ✨")
st.sidebar.markdown("---")

page = st.sidebar.radio(
    "✨ YOUR SPACE",
    [
        "🏠 Dashboard",
        "➕ Add Transaction",
        "📋 Transaction History",
        "📊 Analytics",
        "🎯 Monthly Budget",
    ],
)

st.sidebar.markdown("---")
st.sidebar.info("🌱 Little steps today can build better money habits tomorrow.")

# -------------------------------------------------
# 4. LOAD TRANSACTIONS
# -------------------------------------------------
df = get_transactions()

if not df.empty:
    df["transaction_date"] = pd.to_datetime(
        df["transaction_date"], errors="coerce"
    )
    df = df.dropna(subset=["transaction_date"])
    df["month"] = df["transaction_date"].dt.strftime("%Y-%m")

def get_month_transactions(all_transactions, month_string):
    if all_transactions.empty:
        return all_transactions.copy()
    return all_transactions[all_transactions["month"] == month_string].copy()

def money(value):
    return f"₹{float(value):,.2f}"

# -------------------------------------------------
# 5. DASHBOARD
# -------------------------------------------------
if page == "🏠 Dashboard":
    st.title("🌷 Your Finance Dashboard")
    st.write("👋 Welcome to FinBuddy — let's make your money easier to understand.")
    st.caption("A clear view of your income, spending, and monthly budget. 💚")

    selected_month = st.date_input(
        "🗓️ Choose a month to view",
        value=date.today().replace(day=1),
        key="dashboard_month",
    ).strftime("%Y-%m")

    monthly_df = get_month_transactions(df, selected_month)

    if monthly_df.empty:
        income = 0.0
        expenses = 0.0
    else:
        income = monthly_df.loc[
            monthly_df["transaction_type"] == "Income", "amount"
        ].sum()
        expenses = monthly_df.loc[
            monthly_df["transaction_type"] == "Expense", "amount"
        ].sum()

    # Only the two requested summary cards: no cash flow or savings rate.
    col1, col2 = st.columns(2)
    col1.metric("💚 Total Income", money(income))
    col2.metric("🧡 Total Expenses", money(expenses))

    st.markdown("### 🌈 Your money at a glance")
    left, right = st.columns([1.1, 0.9])

    with left:
        st.subheader("🍩 Where did it go?")
        expense_df = (
            monthly_df[monthly_df["transaction_type"] == "Expense"]
            if not monthly_df.empty
            else pd.DataFrame()
        )

        if not expense_df.empty:
            category_data = expense_df.groupby(
                "category", as_index=False
            )["amount"].sum()
            fig = px.pie(
                category_data,
                names="category",
                values="amount",
                hole=0.58,
                color_discrete_sequence=[
                    "#78C9A5", "#A99AE8", "#F4BE78",
                    "#F08C8C", "#7EB5E8", "#C7A4D8",
                ],
            )
            fig.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                margin=dict(t=15, b=15, l=10, r=10),
                legend_title_text="Categories",
                font=dict(color="#344054"),
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("🌼 No expenses recorded for this month yet. Add one to see your chart!")

    with right:
        st.subheader("🎯 Monthly budget")
        budget = get_budget(selected_month)

        if budget > 0:
            progress = expenses / budget
            st.metric("Your monthly limit", money(budget))
            st.progress(min(progress, 1.0))
            st.caption(f"Spent so far: {money(expenses)}")
            remaining = budget - expenses

            if remaining > 0:
                st.success(f"🎉 {money(remaining)} left in your budget. Keep going!")
            elif remaining == 0:
                st.warning("🌟 You've reached your monthly budget.")
            else:
                st.error(f"🫣 You're over budget by {money(abs(remaining))}.")
        else:
            st.info("💡 Set a monthly budget on the **Monthly Budget** page to track your progress.")

    st.markdown("### 🕒 Recent activity")
    if not monthly_df.empty:
        recent = monthly_df.sort_values(
            ["transaction_date", "id"], ascending=[False, False]
        ).head(5).copy()
        recent["transaction_date"] = recent["transaction_date"].dt.strftime("%d %b %Y")
        display_cols = [
            "transaction_date", "created_at", "transaction_type",
            "category", "amount", "payment_method", "description"
        ]
        recent = recent[[c for c in display_cols if c in recent.columns]]
        recent = recent.rename(columns={
            "transaction_date": "Transaction date",
            "created_at": "Added on",
            "transaction_type": "Type",
            "category": "Category",
            "amount": "Amount (₹)",
            "payment_method": "Payment method",
            "description": "Description",
        })
        st.dataframe(recent, use_container_width=True, hide_index=True)
    else:
        st.info("✨ Your story starts with your first transaction. Head to **Add Transaction**!")

# -------------------------------------------------
# 6. ADD TRANSACTION
# -------------------------------------------------
elif page == "➕ Add Transaction":
    st.title("✨ Add a new transaction")
    st.write("Every little detail helps you understand your money better. 🌿")

    with st.form("add_transaction_form", clear_on_submit=True):
        st.markdown("#### 💫 Transaction details")

        transaction_type = st.radio(
            "What would you like to record?",
            ["Expense 💸", "Income 💚"],
            horizontal=True,
        )
        amount = st.number_input(
            "💰 Amount (₹)",
            min_value=0.01,
            value=10.00,
            step=10.00,
            help="Enter the amount for this transaction.",
        )

        category = st.text_input(
            "🏷️ Your category",
            placeholder="e.g. Groceries, Rent, Salary, Coffee",
            help="Type any category you want. You are not limited to a fixed list.",
        )

        transaction_date = st.date_input(
            "📅 When did the transaction happen?",
            value=date.today(),
        )

        payment_method = st.text_input(
            "💳 Payment method",
            placeholder="e.g. UPI, Cash, Debit card, Bank transfer",
        )

        description = st.text_area(
            "📝 Add a note (optional)",
            placeholder="e.g. Weekly groceries or monthly salary",
            height=90,
        )

        st.caption("🕰️ The app will automatically record the date and time you save this transaction.")

        submitted = st.form_submit_button(
            "💾 Save my transaction ✨",
            use_container_width=True,
        )

        if submitted:
            if not category.strip():
                st.error("🏷️ Please enter a category.")
            elif not payment_method.strip():
                st.error("💳 Please enter a payment method.")
            else:
                saved_at = add_transaction(
                    "Income" if transaction_type.startswith("Income") else "Expense",
                    amount,
                    category.strip(),
                    transaction_date.isoformat(),
                    payment_method.strip(),
                    description.strip(),
                )
                st.success("🎉 Your transaction has been saved!")
                st.info(f"🕰️ Added to FinBuddy on: **{saved_at}**")
                st.toast("Saved successfully! 🌷", icon="💚")

# -------------------------------------------------
# 7. TRANSACTION HISTORY
# -------------------------------------------------
elif page == "📋 Transaction History":
    st.title("📋 Your transaction history")
    st.write("Everything you've recorded, all in one place. 🧾")

    history = get_transactions()

    if history.empty:
        st.info("🌱 No transactions yet. Add your first transaction!")
    else:
        history["transaction_date"] = pd.to_datetime(
            history["transaction_date"], errors="coerce"
        ).dt.strftime("%d %b %Y")

        history = history.rename(columns={
            "id": "ID",
            "transaction_date": "Transaction date",
            "created_at": "Added on",
            "transaction_type": "Type",
            "amount": "Amount (₹)",
            "category": "Category",
            "payment_method": "Payment method",
            "description": "Description",
        })

        st.dataframe(history, use_container_width=True, hide_index=True)

        st.download_button(
            "📥 Download my transactions (CSV)",
            data=history.to_csv(index=False).encode("utf-8"),
            file_name="finbuddy_transactions.csv",
            mime="text/csv",
        )

        st.markdown("### 🗑️ Remove a transaction")
        id_col = "ID"
        selected_id = st.selectbox(
            "Choose the transaction ID to delete",
            history[id_col].tolist(),
            format_func=lambda x: f"Transaction #{x}",
        )
        confirm_delete = st.checkbox("I understand this transaction will be permanently deleted.")

        if st.button("🗑️ Delete selected transaction"):
            if confirm_delete:
                delete_transaction(int(selected_id))
                st.success("Transaction deleted.")
                st.rerun()
            else:
                st.warning("Please confirm before deleting.")

# -------------------------------------------------
# 8. ANALYTICS
# -------------------------------------------------
elif page == "📊 Analytics":
    st.title("📊 Your spending insights")
    st.write("Explore your spending patterns in a simple, visual way. 🌈")

    all_data = get_transactions()

    if all_data.empty:
        st.info("🌱 Add some transactions first to unlock your analytics.")
    else:
        expense_df = all_data[
            all_data["transaction_type"] == "Expense"
        ].copy()

        if not expense_df.empty:
            expense_df["transaction_date"] = pd.to_datetime(
                expense_df["transaction_date"], errors="coerce"
            )
            expense_df = expense_df.dropna(subset=["transaction_date"])

            category_data = expense_df.groupby(
                "category", as_index=False
            )["amount"].sum().sort_values("amount", ascending=False)

            st.subheader("🧁 Spending by category")
            fig = px.bar(
                category_data,
                x="category",
                y="amount",
                color="category",
                color_discrete_sequence=[
                    "#78C9A5", "#A99AE8", "#F4BE78",
                    "#F08C8C", "#7EB5E8", "#C7A4D8",
                ],
                labels={"category": "Category", "amount": "Amount (₹)"},
            )
            fig.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                showlegend=False,
                font=dict(color="#344054"),
            )
            st.plotly_chart(fig, use_container_width=True)

            expense_df["month"] = expense_df["transaction_date"].dt.strftime("%Y-%m")
            monthly_totals = expense_df.groupby(
                "month", as_index=False
            )["amount"].sum().sort_values("month")

            st.subheader("🌷 Monthly spending trend")
            fig2 = px.line(
                monthly_totals,
                x="month",
                y="amount",
                markers=True,
                labels={"month": "Month", "amount": "Expenses (₹)"},
            )
            fig2.update_traces(line=dict(color="#5D9E83", width=4))
            fig2.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#344054"),
            )
            st.plotly_chart(fig2, use_container_width=True)
        else:
            st.info("No expenses to analyse yet. Add an expense to get started.")

# -------------------------------------------------
# 9. MONTHLY BUDGET
# -------------------------------------------------
elif page == "🎯 Monthly Budget":
    st.title("🎯 Your monthly budget")
    st.write("Choose a spending limit that works for you. You've got this! 💚")

    budget_month = st.date_input(
        "🗓️ Select a month",
        value=date.today().replace(day=1),
        key="budget_month_picker",
    ).strftime("%Y-%m")

    existing_budget = get_budget(budget_month)

    with st.form("budget_form"):
        st.markdown("#### 💰 Set your monthly limit")
        new_budget = st.number_input(
            "Monthly budget (₹)",
            min_value=0.0,
            value=float(existing_budget),
            step=500.0,
        )
        budget_submitted = st.form_submit_button(
            "💾 Save my budget",
            use_container_width=True,
        )

        if budget_submitted:
            save_budget(budget_month, new_budget)
            st.success(f"🎉 Budget saved for {budget_month}!")
            st.rerun()

    st.caption("🌱 Your budget is saved separately for each month.")
