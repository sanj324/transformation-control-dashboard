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
    st.info("Upload file to begin analysis.")
    st.stop()

df = load_data(uploaded_file)

if df is None:
    st.stop()

# =====================================================
# SMART DATA CLEANING
# =====================================================

# Convert possible numeric text to numeric
for col in df.columns:
    try:
        df[col] = pd.to_numeric(df[col])
    except:
        pass

# Detect column types
numeric_columns = df.select_dtypes(include=np.number).columns.tolist()
categorical_columns = df.select_dtypes(include="object").columns.tolist()

# Detect date columns
date_columns = []
for col in df.columns:
    try:
        converted = pd.to_datetime(df[col], errors='coerce')
        if converted.notna().sum() > len(df) * 0.6:
            df[col] = converted
            date_columns.append(col)
    except:
        pass

# =====================================================
# DATA PREVIEW
# =====================================================

st.subheader("🔍 Data Preview")
st.dataframe(df, use_container_width=True)

# =====================================================
# AUTO COLUMN SELECTION
# =====================================================

default_numeric = numeric_columns[0] if numeric_columns else None
default_category = categorical_columns[0] if categorical_columns else None
default_date = date_columns[0] if date_columns else None

st.subheader("🧠 Intelligent Column Mapping")

col_amount = st.selectbox(
    "Numeric Column (KPI)",
    ["Auto"] + numeric_columns,
    index=0
)

col_category = st.selectbox(
    "Category Column",
    ["Auto"] + categorical_columns,
    index=0
)

col_date = st.selectbox(
    "Date Column",
    ["Auto"] + date_columns,
    index=0
)

selected_numeric = default_numeric if col_amount == "Auto" else col_amount
selected_category = default_category if col_category == "Auto" else col_category
selected_date = default_date if col_date == "Auto" else col_date

# =====================================================
# FILTER & SORT
# =====================================================

st.subheader("🔎 Filter & Sort")

display_columns = st.multiselect(
    "Select Columns to Display",
    df.columns.tolist(),
    default=df.columns.tolist()
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
# AUTO KPI DASHBOARD
# =====================================================

st.subheader("📈 Intelligent KPI Dashboard")

if selected_numeric:
    total_value = df[selected_numeric].sum()
    avg_value = df[selected_numeric].mean()
    max_value = df[selected_numeric].max()

    col1, col2, col3 = st.columns(3)
    col1.metric("Total", f"{total_value:,.2f}")
    col2.metric("Average", f"{avg_value:,.2f}")
    col3.metric("Maximum", f"{max_value:,.2f}")
else:
    st.warning("No numeric column detected.")

# =====================================================
# CATEGORY ANALYSIS
# =====================================================

if selected_category and selected_numeric:
    grouped = df.groupby(selected_category)[selected_numeric].sum().reset_index()

    fig = px.bar(grouped, x=selected_category, y=selected_numeric,
                 title="Category Analysis")
    st.plotly_chart(fig, use_container_width=True)

# =====================================================
# TIME TREND
# =====================================================

if selected_date and selected_numeric:
    trend = df.groupby(selected_date)[selected_numeric].sum().reset_index()

    fig2 = px.line(trend, x=selected_date, y=selected_numeric,
                   title="Time Trend Analysis")
    st.plotly_chart(fig2, use_container_width=True)

# =====================================================
# ANOMALY DETECTION
# =====================================================

st.subheader("🚨 Anomaly Detection")

if selected_numeric:
    if df[selected_numeric].std() != 0:
        df["Z_Score"] = (
            (df[selected_numeric] - df[selected_numeric].mean())
            / df[selected_numeric].std()
        )

        anomalies = df[np.abs(df["Z_Score"]) > 3]

        st.metric("Anomaly Count", len(anomalies))

        if len(anomalies) > 0:
            st.dataframe(anomalies, use_container_width=True)
    else:
        st.info("Insufficient variance for anomaly detection.")

st.success("🎯 Intelligent Data Engine Active")