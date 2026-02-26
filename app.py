import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
import pdfplumber

st.set_page_config(page_title="Custom Data Dashboard", layout="wide")

st.title("📊 Custom Mapping Data Intelligence Dashboard")

# =====================================================
# FILE UPLOAD
# =====================================================

uploaded_file = st.sidebar.file_uploader(
    "Upload Excel / CSV / PDF File",
    type=["xlsx", "csv", "pdf"]
)

def parse_pdf(file):
    text_data = []
    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            text_data.append(page.extract_text())
    return "\n".join(text_data)

def load_data(file):
    if file.name.endswith(".csv"):
        return pd.read_csv(file)

    elif file.name.endswith(".xlsx"):
        excel = pd.ExcelFile(file)
        sheet = st.sidebar.selectbox("Select Sheet", excel.sheet_names)
        return pd.read_excel(file, sheet_name=sheet)

    elif file.name.endswith(".pdf"):
        text = parse_pdf(file)
        st.subheader("📄 Extracted PDF Text")
        st.text(text[:2000])
        return None

if uploaded_file is None:
    st.info("Upload file to begin.")
    st.stop()

df = load_data(uploaded_file)

if df is None:
    st.stop()

# =====================================================
# DATA PREVIEW
# =====================================================

st.subheader("🔍 Data Preview")
st.dataframe(df, use_container_width=True)

columns = df.columns.tolist()

# =====================================================
# CUSTOM COLUMN MAPPING
# =====================================================

st.subheader("🧭 Custom Dashboard Mapping")

with st.form("mapping_form"):

    col_date = st.selectbox("Select Date Column (Optional)", ["None"] + columns)
    col_numeric = st.selectbox("Select Numeric Column (Required for KPI)", ["None"] + columns)
    col_category = st.selectbox("Select Category Column (Optional)", ["None"] + columns)

    submit_mapping = st.form_submit_button("Apply Mapping")

if not submit_mapping:
    st.info("Select mapping and click Apply Mapping to generate dashboard.")
    st.stop()

# =====================================================
# VALIDATION
# =====================================================

if col_numeric == "None":
    st.error("Numeric column is required for KPI Dashboard.")
    st.stop()

# Clean numeric column
df[col_numeric] = (
    df[col_numeric]
    .astype(str)
    .str.replace(",", "", regex=False)
    .str.replace("₹", "", regex=False)
    .str.replace("$", "", regex=False)
    .str.strip()
)

df[col_numeric] = pd.to_numeric(df[col_numeric], errors="coerce")

# Date conversion if selected
if col_date != "None":
    df[col_date] = pd.to_datetime(df[col_date], errors="coerce")

# =====================================================
# FILTER & SORT
# =====================================================

st.subheader("🔎 Filter & Sort")

display_columns = st.multiselect(
    "Select Columns to Display",
    columns,
    default=columns
)

filtered_df = df[display_columns]

sort_column = st.selectbox("Sort By", display_columns)
sort_order = st.radio("Order", ["Ascending", "Descending"])

filtered_df = filtered_df.sort_values(
    by=sort_column,
    ascending=(sort_order == "Ascending")
)

st.dataframe(filtered_df, use_container_width=True)

# =====================================================
# KPI DASHBOARD
# =====================================================

st.subheader("📈 KPI Dashboard")

if df[col_numeric].notna().sum() == 0:
    st.error("Selected numeric column has no valid numeric data.")
    st.stop()

total_value = df[col_numeric].sum()
avg_value = df[col_numeric].mean()
max_value = df[col_numeric].max()

col1, col2, col3 = st.columns(3)
col1.metric("Total", f"{total_value:,.2f}")
col2.metric("Average", f"{avg_value:,.2f}")
col3.metric("Maximum", f"{max_value:,.2f}")

# =====================================================
# CATEGORY ANALYSIS
# =====================================================

if col_category != "None":

    grouped = df.groupby(col_category)[col_numeric].sum().reset_index()

    fig = px.bar(
        grouped,
        x=col_category,
        y=col_numeric,
        title="Category Analysis"
    )

    st.plotly_chart(fig, use_container_width=True)

# =====================================================
# TIME TREND ANALYSIS
# =====================================================

if col_date != "None":

    trend = df.groupby(col_date)[col_numeric].sum().reset_index()

    fig2 = px.line(
        trend,
        x=col_date,
        y=col_numeric,
        title="Time Trend Analysis"
    )

    st.plotly_chart(fig2, use_container_width=True)

# =====================================================
# ANOMALY DETECTION
# =====================================================

st.subheader("🚨 Anomaly Detection")

std_dev = df[col_numeric].std()

if std_dev and std_dev != 0:

    df["Z_Score"] = (
        (df[col_numeric] - df[col_numeric].mean())
        / std_dev
    )

    anomalies = df[np.abs(df["Z_Score"]) > 3]

    st.metric("Anomaly Count", len(anomalies))

    if len(anomalies) > 0:
        st.dataframe(anomalies, use_container_width=True)
else:
    st.info("Not enough variance for anomaly detection.")

st.success("✅ Custom Dashboard Generated Successfully")