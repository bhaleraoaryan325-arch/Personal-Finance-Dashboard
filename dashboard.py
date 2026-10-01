import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from io import BytesIO

st.set_page_config(
    page_title="Personal Finance Dashboard",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
.stApp {
    background: #0B1220;
}
[data-testid="stSidebar"] {
    background: #111827;
    border-right: 1px solid #263244;
}
.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
}
.hero {
    background: linear-gradient(135deg, #172554, #0F766E);
    padding: 28px 30px;
    border-radius: 20px;
    margin-bottom: 24px;
    border: 1px solid #29405F;
}
.hero h1 {
    margin: 0;
    color: white;
    font-size: 34px;
}
.hero p {
    margin: 8px 0 0;
    color: #C7D2FE;
    font-size: 15px;
}
.metric-card {
    background: #111827;
    border: 1px solid #263244;
    border-radius: 16px;
    padding: 18px;
    min-height: 125px;
}
.metric-label {
    color: #94A3B8;
    font-size: 14px;
    margin-bottom: 8px;
}
.metric-value {
    color: #F8FAFC;
    font-size: 25px;
    font-weight: 700;
}
.metric-positive {
    color: #34D399;
    font-size: 14px;
    margin-top: 8px;
}
.metric-negative {
    color: #FB7185;
    font-size: 14px;
    margin-top: 8px;
}
.section-title {
    color: #F8FAFC;
    font-size: 21px;
    font-weight: 650;
    margin: 20px 0 12px;
}
.info-card {
    background: #111827;
    border: 1px solid #263244;
    border-radius: 16px;
    padding: 18px;
}
.stButton > button, .stDownloadButton > button {
    border-radius: 10px;
}
</style>
""", unsafe_allow_html=True)

def money(value):
    return f"₹{value:,.2f}"

def metric_card(label, value, change=None):
    change_html = ""
    if change is not None:
        cls = "metric-positive" if change >= 0 else "metric-negative"
        symbol = "▲" if change >= 0 else "▼"
        change_html = f'<div class="{cls}">{symbol} {abs(change):.2f}%</div>'
    st.markdown(
        f'<div class="metric-card"><div class="metric-label">{label}</div>'
        f'<div class="metric-value">{value}</div>{change_html}</div>',
        unsafe_allow_html=True
    )

def chart_layout(fig, height=400):
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#CBD5E1"),
        margin=dict(l=10, r=10, t=55, b=10),
        height=height,
        legend=dict(orientation="h", y=-0.15),
        hoverlabel=dict(bgcolor="#111827", font_color="white")
    )
    return fig

st.markdown("""
<div class="hero">
    <h1>💰 Personal Finance & Investment Dashboard</h1>
    <p>Track your portfolio, analyze investments, monitor returns and understand your financial performance.</p>
</div>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("## 💰 Finance Dashboard")
    st.caption("Portfolio analytics")
    st.divider()

    uploaded_file = st.file_uploader(
        "Upload Excel File",
        type=["xlsx"],
        help="The workbook must contain a sheet named Finance_Data."
    )

    st.divider()
    page = st.radio(
        "Navigation",
        ["🏠 Dashboard", "📋 Portfolio", "📊 Analysis"],
        label_visibility="collapsed"
    )

if uploaded_file is None:
    st.info("Upload your Excel file from the sidebar to start analyzing your portfolio.")
    st.markdown("""
    <div class="info-card">
        <h3>Required Excel columns</h3>
        <p>Date · Description · Investment_Type · Investment_Amount · Current_Value · Profit_Loss · Return_Percentage</p>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

try:
    df = pd.read_excel(uploaded_file, sheet_name="Finance_Data")

    required_columns = [
        "Date",
        "Description",
        "Investment_Type",
        "Investment_Amount",
        "Current_Value",
        "Profit_Loss",
        "Return_Percentage"
    ]

    missing_columns = [c for c in required_columns if c not in df.columns]

    if missing_columns:
        st.error("Missing columns: " + ", ".join(missing_columns))
        st.stop()

    for column in ["Investment_Amount", "Current_Value", "Profit_Loss", "Return_Percentage"]:
        df[column] = pd.to_numeric(df[column], errors="coerce").fillna(0)

    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    df["Investment_Type"] = df["Investment_Type"].fillna("Other").astype(str)
    df["Description"] = df["Description"].fillna("Other").astype(str)

    investments = df[df["Investment_Amount"] > 0].copy()

    if investments.empty:
        st.warning("No investment records were found.")
        st.stop()

    with st.sidebar:
        st.markdown("### 🔎 Filters")

        types = sorted(investments["Investment_Type"].unique())
        selected_types = st.multiselect(
            "Investment Type",
            types,
            default=types
        )

        assets = sorted(investments["Description"].unique())
        selected_assets = st.multiselect(
            "Asset",
            assets,
            default=assets
        )

        valid_dates = investments["Date"].dropna()
        if not valid_dates.empty:
            min_date = valid_dates.min().date()
            max_date = valid_dates.max().date()
            date_range = st.date_input(
                "Date Range",
                value=(min_date, max_date),
                min_value=min_date,
                max_value=max_date
            )
        else:
            date_range = None

        st.divider()
        st.caption(f"File: {uploaded_file.name}")
        st.caption(f"Records: {len(investments)}")

    filtered = investments[
        investments["Investment_Type"].isin(selected_types)
        & investments["Description"].isin(selected_assets)
    ].copy()

    if date_range and len(date_range) == 2:
        start_date, end_date = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])
        filtered = filtered[
            filtered["Date"].isna()
            | ((filtered["Date"] >= start_date) & (filtered["Date"] <= end_date))
        ]

    if filtered.empty:
        st.warning("No data matches the selected filters.")
        st.stop()

    total_invested = filtered["Investment_Amount"].sum()
    current_value = filtered["Current_Value"].sum()
    profit_loss = current_value - total_invested
    return_percent = (profit_loss / total_invested * 100) if total_invested else 0
    total_records = len(filtered)

    if page == "🏠 Dashboard":
        st.markdown('<div class="section-title">Portfolio Overview</div>', unsafe_allow_html=True)

        c1, c2, c3, c4 = st.columns(4)
        with c1:
            metric_card("Total Invested", money(total_invested))
        with c2:
            metric_card("Current Value", money(current_value))
        with c3:
            metric_card("Profit / Loss", money(profit_loss))
        with c4:
            metric_card("Overall Return", f"{return_percent:.2f}%")

        st.markdown('<div class="section-title">Portfolio Insights</div>', unsafe_allow_html=True)

        c1, c2, c3 = st.columns(3)
        with c1:
            metric_card("Total Assets", f"{filtered['Description'].nunique():,}")
        with c2:
            metric_card("Investment Types", f"{filtered['Investment_Type'].nunique():,}")
        with c3:
            metric_card("Transactions", f"{total_records:,}")

        left, right = st.columns(2)

        with left:
            type_data = filtered.groupby("Investment_Type", as_index=False)["Investment_Amount"].sum()
            fig = px.pie(
                type_data,
                names="Investment_Type",
                values="Investment_Amount",
                hole=0.58,
                title="Investment Allocation"
            )
            fig.update_traces(textposition="inside", textinfo="percent+label")
            st.plotly_chart(chart_layout(fig, 430), use_container_width=True)

        with right:
            asset_data = (
                filtered.groupby("Description", as_index=False)["Investment_Amount"]
                .sum()
                .sort_values("Investment_Amount", ascending=False)
                .head(10)
            )
            fig = px.bar(
                asset_data,
                x="Investment_Amount",
                y="Description",
                orientation="h",
                title="Top Assets by Investment",
                text="Investment_Amount"
            )
            fig.update_traces(texttemplate="₹%{text:,.0f}", textposition="outside")
            fig.update_xaxes(title="")
            fig.update_yaxes(title="")
            st.plotly_chart(chart_layout(fig, 430), use_container_width=True)

        st.markdown('<div class="section-title">Investment Activity</div>', unsafe_allow_html=True)

        history = (
            filtered.dropna(subset=["Date"])
            .groupby("Date", as_index=False)["Investment_Amount"]
            .sum()
            .sort_values("Date")
        )

        if not history.empty:
            fig = px.area(
                history,
                x="Date",
                y="Investment_Amount",
                title="Investment Activity Over Time"
            )
            fig.update_xaxes(title="")
            fig.update_yaxes(title="Investment Amount")
            st.plotly_chart(chart_layout(fig, 420), use_container_width=True)

    elif page == "📋 Portfolio":
        st.markdown('<div class="section-title">Portfolio Details</div>', unsafe_allow_html=True)

        c1, c2, c3, c4 = st.columns(4)
        with c1:
            metric_card("Invested", money(total_invested))
        with c2:
            metric_card("Current Value", money(current_value))
        with c3:
            metric_card("Profit / Loss", money(profit_loss))
        with c4:
            metric_card("Return", f"{return_percent:.2f}%")

        search = st.text_input("🔍 Search asset or investment type")

        table_data = filtered.copy()

        if search:
            mask = (
                table_data["Description"].str.contains(search, case=False, na=False)
                | table_data["Investment_Type"].str.contains(search, case=False, na=False)
            )
            table_data = table_data[mask]

        display_columns = [
            "Date",
            "Description",
            "Investment_Type",
            "Investment_Amount",
            "Current_Value",
            "Profit_Loss",
            "Return_Percentage"
        ]

        display_data = table_data[display_columns].copy()
        display_data["Date"] = display_data["Date"].dt.strftime("%d-%m-%Y")
        display_data["Investment_Amount"] = display_data["Investment_Amount"].map(lambda x: f"₹{x:,.2f}")
        display_data["Current_Value"] = display_data["Current_Value"].map(lambda x: f"₹{x:,.2f}")
        display_data["Profit_Loss"] = display_data["Profit_Loss"].map(lambda x: f"₹{x:,.2f}")
        display_data["Return_Percentage"] = display_data["Return_Percentage"].map(lambda x: f"{x:.2f}%")

        st.dataframe(display_data, use_container_width=True, hide_index=True)

        export = table_data.copy()
        output = BytesIO()

        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            export.to_excel(writer, index=False, sheet_name="Portfolio")
            pd.DataFrame({
                "Metric": ["Total Invested", "Current Value", "Profit / Loss", "Overall Return", "Records"],
                "Value": [total_invested, current_value, profit_loss, return_percent, len(table_data)]
            }).to_excel(writer, index=False, sheet_name="Summary")

        c1, c2 = st.columns(2)

        with c1:
            st.download_button(
                "📥 Download Excel Report",
                data=output.getvalue(),
                file_name="personal_finance_report.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )

        with c2:
            csv_data = table_data.to_csv(index=False).encode("utf-8")
            st.download_button(
                "📥 Download CSV",
                data=csv_data,
                file_name="portfolio_data.csv",
                mime="text/csv",
                use_container_width=True
            )

    elif page == "📊 Analysis":
        st.markdown('<div class="section-title">Investment Analysis</div>', unsafe_allow_html=True)

        type_data = (
            filtered.groupby("Investment_Type", as_index=False)[
                ["Investment_Amount", "Current_Value", "Profit_Loss"]
            ].sum()
        )

        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=type_data["Investment_Type"],
            y=type_data["Investment_Amount"],
            name="Invested"
        ))
        fig.add_trace(go.Bar(
            x=type_data["Investment_Type"],
            y=type_data["Current_Value"],
            name="Current Value"
        ))
        fig.update_layout(
            barmode="group",
            title="Invested Amount vs Current Value",
            xaxis_title="Investment Type",
            yaxis_title="Amount"
        )
        st.plotly_chart(chart_layout(fig, 440), use_container_width=True)

        left, right = st.columns(2)

        with left:
            asset_profit = (
                filtered.groupby("Description", as_index=False)["Profit_Loss"]
                .sum()
                .sort_values("Profit_Loss", ascending=False)
                .head(10)
            )
            fig = px.bar(
                asset_profit,
                x="Profit_Loss",
                y="Description",
                orientation="h",
                title="Profit / Loss by Asset",
                color="Profit_Loss",
                color_continuous_scale=["#FB7185", "#64748B", "#34D399"]
            )
            fig.update_xaxes(title="")
            fig.update_yaxes(title="")
            st.plotly_chart(chart_layout(fig, 440), use_container_width=True)

        with right:
            returns = (
                filtered.groupby("Description", as_index=False)["Return_Percentage"]
                .mean()
                .sort_values("Return_Percentage", ascending=False)
                .head(10)
            )
            fig = px.bar(
                returns,
                x="Return_Percentage",
                y="Description",
                orientation="h",
                title="Average Return by Asset",
                text="Return_Percentage"
            )
            fig.update_traces(texttemplate="%{text:.2f}%", textposition="outside")
            fig.update_xaxes(title="Return %")
            fig.update_yaxes(title="")
            st.plotly_chart(chart_layout(fig, 440), use_container_width=True)

        history = (
            filtered.dropna(subset=["Date"])
            .groupby("Date", as_index=False)[
                ["Investment_Amount", "Current_Value"]
            ].sum()
            .sort_values("Date")
        )

        if not history.empty:
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=history["Date"],
                y=history["Investment_Amount"],
                mode="lines+markers",
                name="Invested Amount"
            ))
            fig.add_trace(go.Scatter(
                x=history["Date"],
                y=history["Current_Value"],
                mode="lines+markers",
                name="Current Value"
            ))
            fig.update_layout(
                title="Portfolio Value Trend",
                xaxis_title="Date",
                yaxis_title="Amount"
            )
            st.plotly_chart(chart_layout(fig, 440), use_container_width=True)

        st.markdown('<div class="section-title">Investment Type Summary</div>', unsafe_allow_html=True)

        summary = (
            filtered.groupby("Investment_Type", as_index=False)
            .agg(
                Invested=("Investment_Amount", "sum"),
                Current_Value=("Current_Value", "sum"),
                Profit_Loss=("Profit_Loss", "sum")
            )
        )
        summary["Return %"] = summary.apply(
            lambda row: (row["Profit_Loss"] / row["Invested"] * 100) if row["Invested"] else 0,
            axis=1
        )

        st.dataframe(
            summary.style.format({
                "Invested": "₹{:,.2f}",
                "Current_Value": "₹{:,.2f}",
                "Profit_Loss": "₹{:,.2f}",
                "Return %": "{:.2f}%"
            }),
            use_container_width=True,
            hide_index=True
        )

except ValueError:
    st.error("The Finance_Data sheet was not found in the Excel file or the data format is incorrect.")
except Exception as e:
    st.error(f"Error: {e}")
