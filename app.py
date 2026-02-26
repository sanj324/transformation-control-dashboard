import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
import pdfplumber

st.set_page_config(page_title="Universal Data Intelligence Dashboard", layout="wide")

st.title("📊 Universal Data Intelligence Dashboard")

# =====================================================
# FILE UPLOAD
# =====================================================

uploaded_file = st.sidebar.file_uploader(
    "Upload Excel / CSV / PDF File",
    type=["xlsx", "csv", "pdf"]
)

def parse_pdf(file):
    all_text = []
    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            all_text.append(page.extract_text())
    return "\n".join(all_text)

def load_data(file):
    if file.name.endswith(".csv"):
        return pd.read_csv(file)

    elif file.name.endswith(".xlsx"):
        excel = pd.ExcelFile(file)
        sheet = st.sidebar.selectbox("Select Sheet", excel.sheet_names)
        return pd.read_excel(file, sheet_name=sheet)

    elif file.name.endswith(".pdf"):
        text = parse_pdf(file)
        st.subheader("📄 Extracted PDF Text Preview")
        st.text(text[:2000])
        return None

    else:
        st.error("Unsupported file type")
        return None

if uploaded_file is None:
    st.info("Upload file to begin analysis.")
    st.stop()

df = load_data(uploaded_file)

if df is None:
    st.stop()

# =====================================================
# DATA PREVIEW
# =====================================================

st.subheader("🔍 Data Preview")
st.dataframe(df, use_container_width=True)

# =====================================================
# COLUMN MAPPING
# =====================================================

st.subheader("🧠 Column Mapping")

columns = df.columns.tolist()

col_date = st.selectbox("Select Date Column (Optional)", ["None"] + columns)
col_amount = st.selectbox("Select Numeric Column for KPI", ["None"] + columns)
col_category = st.selectbox("Select Category Column", ["None"] + columns)

# =====================================================
# FILTER SECTION
# =====================================================

st.subheader("🔎 Filter & Sort")

selected_columns = st.multiselect("Select Columns to Display", columns, default=columns)

filtered_df = df[selected_columns]

sort_column = st.selectbox("Sort By", selected_columns)
sort_order = st.radio("Order", ["Ascending", "Descending"])

filtered_df = filtered_df.sort_values(
    by=sort_column,
    ascending=(sort_order == "Ascending")
)

st.dataframe(filtered_df, use_container_width=True)

# =====================================================
# KPI SECTION
# =====================================================

st.subheader("📈 Auto KPI Dashboard")

if col_amount != "None":
    total_value = df[col_amount].sum()
    avg_value = df[col_amount].mean()
    max_value = df[col_amount].max()

    col1, col2, col3 = st.columns(3)
    col1.metric("Total", f"{total_value:,.2f}")
    col2.metric("Average", f"{avg_value:,.2f}")
    col3.metric("Maximum", f"{max_value:,.2f}")

# =====================================================
# CATEGORY CHART
# =====================================================

if col_category != "None" and col_amount != "None":
    grouped = df.groupby(col_category)[col_amount].sum().reset_index()

    fig = px.bar(grouped, x=col_category, y=col_amount, title="Category Analysis")
    st.plotly_chart(fig, use_container_width=True)

# =====================================================
# ANOMALY DETECTION
# =====================================================

st.subheader("🚨 Anomaly Detection")

if col_amount != "None":
    df["Z_Score"] = (df[col_amount] - df[col_amount].mean()) / df[col_amount].std()

    anomalies = df[np.abs(df["Z_Score"]) > 3]

    st.metric("Anomaly Count", len(anomalies))

    if len(anomalies) > 0:
        st.dataframe(anomalies, use_container_width=True)

# =====================================================
# DATE TREND
# =====================================================

if col_date != "None" and col_amount != "None":
    df[col_date] = pd.to_datetime(df[col_date], errors='coerce')

    trend = df.groupby(col_date)[col_amount].sum().reset_index()

    fig2 = px.line(trend, x=col_date, y=col_amount, title="Time Trend Analysis")
    st.plotly_chart(fig2, use_container_width=True)

st.success("🎯 Universal Data Intelligence Engine Active")