import streamlit as st
import pandas as pd
import plotly.express as px
from io import BytesIO

st.set_page_config(
    page_title="Personal Finance Dashboard",
    page_icon="📊",
    layout="wide"
)

st.markdown("""
<style>
.stApp {
    background-color: #0E1117;
    color: #FFFFFF;
}
[data-testid="stSidebar"] {
    background-color: #161B27;
}
[data-testid="stMetric"] {
    background-color: #1C2333;
    padding: 20px;
    border-radius: 12px;
    border: 1px solid #303A50;
}
[data-testid="stMetricValue"] {
    color: #00D4AA;
}
h1, h2, h3 {
    color: #FFFFFF;
}
</style>
""", unsafe_allow_html=True)

st.title("📊 Personal Finance & Investment Portfolio")
st.caption("Your Personal Investment Analytics Dashboard")

st.subheader("📂 Upload Your Investment Data")

uploaded_file = st.file_uploader(
    "Select Your Excel File",
    type=["xlsx"]
)

if uploaded_file is None:
    st.info("Please upload an Excel file to view your dashboard.")
    st.stop()

try:
    df = pd.read_excel(
        uploaded_file,
        sheet_name="Finance_Data"
    )

    required_columns = [
        "Date",
        "Description",
        "Investment_Type",
        "Investment_Amount",
        "Current_Value",
        "Profit_Loss",
        "Return_Percentage"
    ]

    missing_columns = [
        col for col in required_columns
        if col not in df.columns
    ]

    if missing_columns:
        st.error(
            "The following columns are missing from the Excel file: "
            + ", ".join(missing_columns)
        )
        st.stop()

    df["Investment_Amount"] = pd.to_numeric(
        df["Investment_Amount"], errors="coerce"
    ).fillna(0)

    df["Current_Value"] = pd.to_numeric(
        df["Current_Value"], errors="coerce"
    ).fillna(0)

    df["Profit_Loss"] = pd.to_numeric(
        df["Profit_Loss"], errors="coerce"
    ).fillna(0)

    df["Return_Percentage"] = pd.to_numeric(
        df["Return_Percentage"], errors="coerce"
    ).fillna(0)

    df["Date"] = pd.to_datetime(
        df["Date"], errors="coerce"
    )

    investments = df[
        df["Investment_Amount"] > 0
    ].copy()

    if investments.empty:
        st.warning("No investment data was found in the Excel file.")
        st.stop()

    investments["Investment_Type"] = (
        investments["Investment_Type"]
        .fillna("Other")
        .astype(str)
    )

    investments["Description"] = (
        investments["Description"]
        .fillna("Other")
        .astype(str)
    )

    st.sidebar.title("📊 Navigation")

    page = st.sidebar.radio(
        "Select Page",
        [
            "Home",
            "Portfolio",
            "Investment Analysis"
        ]
    )

    st.sidebar.divider()

    st.sidebar.write("📁 Uploaded File")
    st.sidebar.write(uploaded_file.name)

    st.sidebar.write(
        f"Total Records: {len(investments)}"
    )

    st.divider()

    st.subheader("🔎 Investment Filters")

    col1, col2 = st.columns(2)

    investment_types = sorted(
        investments["Investment_Type"].unique()
    )

    with col1:
        selected_types = st.multiselect(
            "Investment Type",
            investment_types,
            default=investment_types
        )

    with col2:
        assets = sorted(
            investments["Description"].unique()
        )

        selected_assets = st.multiselect(
            "Asset Name",
            assets,
            default=assets
        )

    filtered = investments[
        investments["Investment_Type"].isin(selected_types)
        & investments["Description"].isin(selected_assets)
    ].copy()

    if filtered.empty:
        st.warning("No data found for the selected filters.")
        st.stop()

    total_invested = filtered["Investment_Amount"].sum()

    current_value = filtered["Current_Value"].sum()

    profit_loss = current_value - total_invested

    return_percent = (
        profit_loss / total_invested * 100
        if total_invested > 0 else 0
    )

    if page == "Home":

        st.header("🏠 Portfolio Overview")

        col1, col2, col3, col4 = st.columns(4)

        col1.metric(
            "Total Invested",
            f"₹{total_invested:,.2f}"
        )

        col2.metric(
            "Current Portfolio Value",
            f"₹{current_value:,.2f}"
        )

        col3.metric(
            "Total Profit / Loss",
            f"₹{profit_loss:,.2f}"
        )

        col4.metric(
            "Overall Return",
            f"{return_percent:.2f}%"
        )

        st.divider()

        st.subheader("📈 Investment Distribution")

        type_data = (
            filtered.groupby("Investment_Type")["Investment_Amount"]
            .sum()
            .reset_index()
        )

        fig1 = px.pie(
            type_data,
            names="Investment_Type",
            values="Investment_Amount",
            hole=0.5,
            title="Investment Type-wise Distribution"
        )

        fig1.update_layout(
            template="plotly_dark",
            paper_bgcolor="#0E1117",
            plot_bgcolor="#0E1117"
        )

        st.plotly_chart(
            fig1,
            use_container_width=True
        )

        st.subheader("💰 Asset-wise Investment")

        asset_data = (
            filtered.groupby("Description")["Investment_Amount"]
            .sum()
            .reset_index()
            .sort_values("Investment_Amount", ascending=False)
        )

        fig2 = px.bar(
            asset_data,
            x="Description",
            y="Investment_Amount",
            title="Investment by Asset",
            color="Investment_Amount"
        )

        fig2.update_layout(
            template="plotly_dark",
            paper_bgcolor="#0E1117",
            plot_bgcolor="#0E1117"
        )

        st.plotly_chart(
            fig2,
            use_container_width=True
        )

    elif page == "Portfolio":

        st.header("📋 Complete Portfolio")

        col1, col2, col3, col4 = st.columns(4)

        col1.metric(
            "Total Invested",
            f"₹{total_invested:,.2f}"
        )

        col2.metric(
            "Current Value",
            f"₹{current_value:,.2f}"
        )

        col3.metric(
            "Profit / Loss",
            f"₹{profit_loss:,.2f}"
        )

        col4.metric(
            "Return",
            f"{return_percent:.2f}%"
        )

        st.divider()

        search = st.text_input(
            "🔍 Search Asset Name"
        )

        table_data = filtered.copy()

        if search:
            table_data = table_data[
                table_data["Description"].str.contains(
                    search,
                    case=False,
                    na=False
                )
            ]

        display_columns = [
            "Date",
            "Description",
            "Investment_Type",
            "Investment_Amount",
            "Current_Value",
            "Profit_Loss",
            "Return_Percentage"
        ]

        st.dataframe(
            table_data[display_columns],
            use_container_width=True,
            hide_index=True
        )

        output = BytesIO()

        with pd.ExcelWriter(
            output,
            engine="openpyxl"
        ) as writer:
            table_data.to_excel(
                writer,
                index=False,
                sheet_name="Portfolio"
            )

        st.download_button(
            label="📥 Download Portfolio Excel",
            data=output.getvalue(),
            file_name="portfolio_analysis.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    elif page == "Investment Analysis":

        st.header("📈 Investment Analysis")

        col1, col2 = st.columns(2)

        with col1:
            st.metric(
                "Total Invested",
                f"₹{total_invested:,.2f}"
            )

        with col2:
            st.metric(
                "Current Portfolio Value",
                f"₹{current_value:,.2f}"
            )

        st.divider()

        st.subheader("📊 Investment Type Analysis")

        type_data = (
            filtered.groupby("Investment_Type")[
                ["Investment_Amount", "Current_Value"]
            ]
            .sum()
            .reset_index()
        )

        fig3 = px.bar(
            type_data,
            x="Investment_Type",
            y=["Investment_Amount", "Current_Value"],
            barmode="group",
            title="Invested Amount vs Current Value"
        )

        fig3.update_layout(
            template="plotly_dark",
            paper_bgcolor="#0E1117",
            plot_bgcolor="#0E1117"
        )

        st.plotly_chart(
            fig3,
            use_container_width=True
        )

        st.subheader("📅 Investment Activity Over Time")

        history = (
            filtered.dropna(subset=["Date"])
            .groupby("Date")["Investment_Amount"]
            .sum()
            .reset_index()
            .sort_values("Date")
        )

        fig4 = px.line(
            history,
            x="Date",
            y="Investment_Amount",
            markers=True,
            title="Investment History"
        )

        fig4.update_layout(
            template="plotly_dark",
            paper_bgcolor="#0E1117",
            plot_bgcolor="#0E1117"
        )

        st.plotly_chart(
            fig4,
            use_container_width=True
        )

        st.subheader("💹 Profit / Loss by Asset")

        asset_profit = (
            filtered.groupby("Description")["Profit_Loss"]
            .sum()
            .reset_index()
            .sort_values("Profit_Loss", ascending=False)
        )

        fig5 = px.bar(
            asset_profit,
            x="Description",
            y="Profit_Loss",
            color="Profit_Loss",
            title="Asset-wise Profit / Loss"
        )

        fig5.update_layout(
            template="plotly_dark",
            paper_bgcolor="#0E1117",
            plot_bgcolor="#0E1117"
        )

        st.plotly_chart(
            fig5,
            use_container_width=True
        )

except ValueError:
    st.error(
        "The Finance_Data sheet was not found in the Excel file "
        "or the data format is incorrect."
    )

except Exception as e:
    st.error(f"Error: {e}")