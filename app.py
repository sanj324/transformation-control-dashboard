import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
import pdfplumber
import json

st.set_page_config(page_title="Enterprise Data Dashboard", layout="wide")

st.title("📊 Enterprise Custom Data Intelligence Platform")

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

st.subheader("🔍 Data Preview")
st.dataframe(df, use_container_width=True)

columns = df.columns.tolist()

# =====================================================
# MAPPING PROFILE MANAGEMENT
# =====================================================

st.subheader("🧭 Dashboard Mapping Configuration")

with st.form("mapping_form"):

    col_date = st.selectbox("Select Date Column (Optional)", ["None"] + columns)
    col_numeric = st.selectbox("Select Numeric Column (Required)", ["None"] + columns)
    col_category = st.selectbox("Select Category Column (Optional)", ["None"] + columns)

    save_mapping = st.form_submit_button("Apply & Save Mapping")

if save_mapping:

    if col_numeric == "None":
        st.error("Numeric column is required.")
        st.stop()

    st.session_state["mapping"] = {
        "date": col_date,
        "numeric": col_numeric,
        "category": col_category
    }

if "mapping" not in st.session_state:
    st.warning("Please configure mapping first.")
    st.stop()

mapping = st.session_state["mapping"]

# Allow download of mapping profile
mapping_json = json.dumps(mapping)
st.download_button(
    "⬇ Download Mapping Profile",
    mapping_json,
    file_name="mapping_profile.json"
)

# Upload mapping profile
uploaded_mapping = st.sidebar.file_uploader(
    "Upload Mapping Profile (.json)",
    type=["json"]
)

if uploaded_mapping:
    mapping = json.load(uploaded_mapping)
    st.session_state["mapping"] = mapping
    st.success("Mapping profile loaded successfully.")

col_date = mapping["date"]
col_numeric = mapping["numeric"]
col_category = mapping["category"]

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

if col_date != "None":
    df[col_date] = pd.to_datetime(df[col_date], errors="coerce")

# =====================================================
# DASHBOARD TABS
# =====================================================

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📈 KPI Overview",
    "📊 Category Analysis",
    "📅 Time Trend",
    "🚨 Anomaly Detection",
    "📋 Data Explorer"
])

# =====================================================
# TAB 1 - KPI
# =====================================================

with tab1:

    if df[col_numeric].notna().sum() == 0:
        st.error("No valid numeric data.")
    else:
        total_value = df[col_numeric].sum()
        avg_value = df[col_numeric].mean()
        max_value = df[col_numeric].max()

        c1, c2, c3 = st.columns(3)
        c1.metric("Total", f"{total_value:,.2f}")
        c2.metric("Average", f"{avg_value:,.2f}")
        c3.metric("Maximum", f"{max_value:,.2f}")

# =====================================================
# TAB 2 - CATEGORY
# =====================================================

with tab2:

    if col_category != "None":
        grouped = df.groupby(col_category)[col_numeric].sum().reset_index()
        fig = px.bar(grouped, x=col_category, y=col_numeric)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No category column selected.")

# =====================================================
# TAB 3 - TIME TREND
# =====================================================

with tab3:

    if col_date != "None":
        trend = df.groupby(col_date)[col_numeric].sum().reset_index()
        fig2 = px.line(trend, x=col_date, y=col_numeric)
        st.plotly_chart(fig2, use_container_width=True)
    else:
        st.info("No date column selected.")

# =====================================================
# TAB 4 - ANOMALY
# =====================================================

with tab4:

    std_dev = df[col_numeric].std()

    if std_dev and std_dev != 0:
        df["Z_Score"] = (
            (df[col_numeric] - df[col_numeric].mean())
            / std_dev
        )
        anomalies = df[np.abs(df["Z_Score"]) > 3]

        st.metric("Anomaly Count", len(anomalies))
        if len(anomalies) > 0:
            st.dataframe(anomalies)
    else:
        st.info("Not enough variance for anomaly detection.")

# =====================================================
# TAB 5 - DATA EXPLORER
# =====================================================

with tab5:

    display_columns = st.multiselect(
        "Select Columns",
        columns,
        default=columns
    )

    sort_column = st.selectbox("Sort By", display_columns)
    sort_order = st.radio("Order", ["Ascending", "Descending"])

    filtered_df = df[display_columns].sort_values(
        by=sort_column,
        ascending=(sort_order == "Ascending")
    )

    st.dataframe(filtered_df, use_container_width=True)

st.success("🎯 Enterprise Dashboard Ready")