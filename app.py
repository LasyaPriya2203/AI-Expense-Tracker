import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import date

from database import (
    init_db,
    add_expense,
    get_expenses,
    delete_expense,
    add_or_update_budget,
    get_budgets
)

from ai_service import (
    categorize_expense,
    generate_insights,
    ask_ai,
    analyze_receipt
)


# -----------------------------
# PAGE CONFIGURATION
# -----------------------------

st.set_page_config(
    page_title="AI Expense Tracker",
    page_icon="💰",
    layout="wide"
)


# -----------------------------
# INITIALIZE DATABASE
# -----------------------------

init_db()


# -----------------------------
# CONSTANTS
# -----------------------------

CATEGORIES = [
    "Food",
    "Transportation",
    "Groceries",
    "Shopping",
    "Rent",
    "Utilities",
    "Education",
    "Healthcare",
    "Entertainment",
    "Travel",
    "Subscriptions",
    "Other"
]

PAYMENT_METHODS = [
    "Cash",
    "UPI",
    "Credit Card",
    "Debit Card",
    "Bank Transfer",
    "Other"
]


# -----------------------------
# LOAD EXPENSES
# -----------------------------

def load_data():

    rows = get_expenses()

    columns = [
        "id",
        "amount",
        "category",
        "merchant",
        "description",
        "expense_date",
        "payment_method"
    ]

    df = pd.DataFrame(
        rows,
        columns=columns
    )

    if not df.empty:

        df["expense_date"] = pd.to_datetime(
            df["expense_date"]
        )

    return df


df = load_data()


# -----------------------------
# SIDEBAR
# -----------------------------

st.sidebar.title("💰 AI Expense Tracker")

st.sidebar.write(
    "Your intelligent personal finance manager"
)

page = st.sidebar.radio(
    "Menu",
    [
        "🏠 Dashboard",
        "➕ Add Expense",
        "📷 Scan Receipt",
        "📋 Expenses",
        "📊 Analytics",
        "🎯 Budgets"
    ]
)


# =====================================================
# DASHBOARD
# =====================================================

if page == "🏠 Dashboard":

    st.title("💰 AI Expense Tracker")

    st.subheader(
        "Smart spending management powered by AI"
    )

    st.divider()

    if df.empty:

        st.info(
            "👋 Welcome! You haven't added any expenses yet."
        )

        st.write(
            "Use **Add Expense** from the left menu "
            "to add your first expense."
        )

        col1, col2, col3 = st.columns(3)

        col1.info("➕ Add expenses")

        col2.info("📷 Scan receipts")

        col3.info("🤖 Get AI insights")

    else:

        total = df["amount"].sum()

        current_month = pd.Timestamp.today().strftime(
            "%Y-%m"
        )

        month_df = df[
            df["expense_date"].dt.strftime(
                "%Y-%m"
            ) == current_month
        ]

        month_total = month_df["amount"].sum()

        average = df["amount"].mean()

        highest = df["amount"].max()

        c1, c2, c3, c4 = st.columns(4)

        c1.metric(
            "💰 Total",
            f"₹{total:,.2f}"
        )

        c2.metric(
            "📅 This Month",
            f"₹{month_total:,.2f}"
        )

        c3.metric(
            "📊 Average",
            f"₹{average:,.2f}"
        )

        c4.metric(
            "🔝 Highest",
            f"₹{highest:,.2f}"
        )

        st.divider()

        col1, col2 = st.columns(2)

        with col1:

            st.subheader(
                "📊 Spending by Category"
            )

            category_data = (
                df.groupby("category")["amount"]
                .sum()
                .reset_index()
            )

            fig = px.pie(
                category_data,
                names="category",
                values="amount",
                hole=0.4
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

        with col2:

            st.subheader(
                "🧾 Recent Expenses"
            )

            recent = df.head(8).copy()

            st.dataframe(
                recent[
                    [
                        "expense_date",
                        "merchant",
                        "category",
                        "amount"
                    ]
                ],
                use_container_width=True,
                hide_index=True
            )


# =====================================================
# ADD EXPENSE
# =====================================================

elif page == "➕ Add Expense":

    st.title("➕ Add Expense")

    st.write(
        "Add a new expense manually."
    )

    with st.form("add_expense_form"):

        amount = st.number_input(
            "Amount (₹)",
            min_value=0.0,
            step=10.0
        )

        merchant = st.text_input(
            "Merchant",
            placeholder="Example: Zomato"
        )

        description = st.text_input(
            "Description",
            placeholder="Example: Dinner"
        )

        category = st.selectbox(
            "Category",
            CATEGORIES
        )

        payment_method = st.selectbox(
            "Payment Method",
            PAYMENT_METHODS
        )

        expense_date = st.date_input(
            "Date",
            date.today()
        )

        ai_category = st.checkbox(
            "🤖 Let AI categorize this expense"
        )

        submitted = st.form_submit_button(
            "💾 Save Expense"
        )

        if submitted:

            if amount <= 0:

                st.error(
                    "Enter an amount greater than zero."
                )

            else:

                final_category = category

                if ai_category:

                    with st.spinner(
                        "🤖 AI is analyzing..."
                    ):

                        result = categorize_expense(
                            description,
                            merchant,
                            amount
                        )

                    if result["category"] in CATEGORIES:

                        final_category = result[
                            "category"
                        ]

                    st.info(
                        f"AI Category: {final_category}"
                    )

                add_expense(
                    amount,
                    final_category,
                    merchant,
                    description,
                    str(expense_date),
                    payment_method
                )

                st.success(
                    "✅ Expense saved successfully!"
                )

                st.rerun()


# =====================================================
# RECEIPT SCANNER
# =====================================================

elif page == "📷 Scan Receipt":

    st.title("📷 AI Receipt Scanner")

    st.write(
        "Upload a receipt and AI will extract the details."
    )

    uploaded = st.file_uploader(
        "Choose a receipt image",
        type=[
            "png",
            "jpg",
            "jpeg"
        ]
    )

    if uploaded:

        st.image(
            uploaded,
            width=450
        )

        if st.button(
            "🤖 Analyze Receipt"
        ):

            with st.spinner(
                "Reading receipt with AI..."
            ):

                result = analyze_receipt(
                    uploaded
                )

            st.session_state[
                "receipt"
            ] = result

    if "receipt" in st.session_state:

        result = st.session_state[
            "receipt"
        ]

        st.divider()

        st.subheader(
            "🤖 AI Result"
        )

        merchant = st.text_input(
            "Merchant",
            value=result.get(
                "merchant",
                ""
            )
        )

        amount = st.number_input(
            "Amount",
            value=float(
                result.get(
                    "amount",
                    0
                ) or 0
            )
        )

        category = st.selectbox(
            "Category",
            CATEGORIES
        )

        description = st.text_input(
            "Description",
            value=result.get(
                "description",
                ""
            )
        )

        payment_method = st.selectbox(
            "Payment Method",
            PAYMENT_METHODS
        )

        if st.button(
            "💾 Save Receipt Expense"
        ):

            add_expense(
                amount,
                category,
                merchant,
                description,
                str(date.today()),
                payment_method
            )

            st.success(
                "✅ Receipt expense saved!"
            )

            del st.session_state[
                "receipt"
            ]

            st.rerun()


# =====================================================
# EXPENSE LIST
# =====================================================

elif page == "📋 Expenses":

    st.title("📋 Expenses")

    if df.empty:

        st.info(
            "No expenses found."
        )

    else:

        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True
        )

        st.divider()

        st.subheader(
            "🗑 Delete Expense"
        )

        expense_id = st.number_input(
            "Enter Expense ID",
            min_value=1,
            step=1
        )

        if st.button(
            "Delete"
        ):

            delete_expense(
                expense_id
            )

            st.success(
                "Expense deleted."
            )

            st.rerun()


# =====================================================
# ANALYTICS
# =====================================================

elif page == "📊 Analytics":

    st.title("📊 Analytics")

    if df.empty:

        st.info(
            "Add expenses to view analytics."
        )

    else:

        category_data = (
            df.groupby("category")["amount"]
            .sum()
            .reset_index()
        )

        st.subheader(
            "Spending by Category"
        )

        fig = px.bar(
            category_data,
            x="category",
            y="amount",
            text_auto=True
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

        df["month"] = (
            df["expense_date"]
            .dt.to_period("M")
            .astype(str)
        )

        monthly = (
            df.groupby("month")["amount"]
            .sum()
            .reset_index()
        )

        st.subheader(
            "Monthly Spending"
        )

        fig2 = px.line(
            monthly,
            x="month",
            y="amount",
            markers=True
        )

        st.plotly_chart(
            fig2,
            use_container_width=True
        )


# =====================================================
# BUDGETS
# =====================================================

elif page == "🎯 Budgets":

    st.title("🎯 Budgets")

    month = date.today().strftime(
        "%Y-%m"
    )

    category = st.selectbox(
        "Category",
        CATEGORIES
    )

    budget = st.number_input(
        "Budget (₹)",
        min_value=0.0,
        step=500.0
    )

    if st.button(
        "💾 Save Budget"
    ):

        if budget > 0:

            add_or_update_budget(
                category,
                budget,
                month
            )

            st.success(
                "Budget saved!"
            )

            st.rerun()

    st.divider()

    budgets = get_budgets(
        month
    )

    if budgets:

        for cat, amount in budgets:

            spent = 0

            if not df.empty:

                spent = df[
                    (
                        df["category"] == cat
                    )
                    &
                    (
                        df["expense_date"]
                        .dt.strftime("%Y-%m")
                        == month
                    )
                ]["amount"].sum()

            st.subheader(cat)

            progress = min(
                spent / amount,
                1
            ) if amount > 0 else 0

            st.progress(progress)

            st.write(
                f"Spent: ₹{spent:,.2f} / "
                f"₹{amount:,.2f}"
            )

            if spent > amount:

                st.error(
                    "🚨 Budget exceeded!"
                )

            elif spent >= amount * 0.8:

                st.warning(
                    "⚠️ You are close to your budget."
                )

            else:

                st.success(
                    "✅ Within budget."
                )

    else:

        st.info(
            "No budgets created."
        )


# =====================================================
# AI ASSISTANT
# =====================================================

elif page == "🤖 AI Assistant":

    st.title("🤖 AI Expense Assistant")

    st.write(
        "Ask questions about your expenses."
    )

    question = st.chat_input(
        "Example: How much did I spend on food?"
    )

    if question:

        with st.chat_message(
            "user"
        ):

            st.write(question)

        with st.chat_message(
            "assistant"
        ):

            data = df.to_string(
                index=False
            ) if not df.empty else "No expenses."

            with st.spinner(
                "Thinking..."
            ):

                answer = ask_ai(
                    question,
                    data
                )

            st.write(answer)


# =====================================================
# AI INSIGHTS
# =====================================================

elif page == "💡 AI Insights":

    st.title("💡 AI Financial Insights")

    if df.empty:

        st.info(
            "Add expenses before generating insights."
        )

    else:

        st.write(
            "Let AI analyze your spending patterns."
        )

        if st.button(
            "🤖 Generate Insights"
        ):

            data = df.to_string(
                index=False
            )

            with st.spinner(
                "AI is analyzing your expenses..."
            ):

                insights = generate_insights(
                    data
                )

            st.markdown(
                insights
            )