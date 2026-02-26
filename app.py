import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
import pdfplumber
import json

# ======================================================
# PAGE CONFIG
# ======================================================

st.set_page_config(
    page_title="Enterprise AI Data Platform",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ======================================================
# CUSTOM STYLING
# ======================================================

st.markdown("""
<style>
.main {background-color: #f5f7fa;}
h1 {color: #1f2937;}
h2 {color: #374151;}
.stMetric {background-color: white; padding: 15px; border-radius: 10px;}
div[data-testid="stTabs"] button {font-size:16px;}
</style>
""", unsafe_allow_html=True)

# ======================================================
# HEADER
# ======================================================

st.title("🚀 Enterprise AI Data Intelligence Platform")
st.caption("Custom Mapping • KPI Dashboard • Anomaly Detection • AI Governance")

# ======================================================
# SIDEBAR – FILE UPLOAD
# ======================================================

st.sidebar.header("📂 Data Upload")

uploaded_file = st.sidebar.file_uploader(
    "Upload Excel / CSV / PDF",
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
        st.subheader("📄 Extracted PDF Preview")
        st.text(text[:1500])
        return None

if uploaded_file is None:
    st.info("👈 Upload a dataset to begin.")
    st.stop()

df = load_data(uploaded_file)

if df is None:
    st.stop()

# ======================================================
# DATA PREVIEW
# ======================================================

st.subheader("🔍 Data Preview")
st.dataframe(df, use_container_width=True)

columns = df.columns.tolist()

# ======================================================
# MAPPING CONFIGURATION
# ======================================================

st.subheader("🧭 Dashboard Column Mapping")

with st.form("mapping_form"):

    col_date = st.selectbox("Date Column (Optional)", ["None"] + columns)
    col_numeric = st.selectbox("Numeric Column (Required)", ["None"] + columns)
    col_category = st.selectbox("Category Column (Optional)", ["None"] + columns)

    submit_mapping = st.form_submit_button("Apply Mapping")

if not submit_mapping:
    st.warning("Select mapping and click Apply Mapping.")
    st.stop()

if col_numeric == "None":
    st.error("Numeric column is required.")
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

if col_date != "None":
    df[col_date] = pd.to_datetime(df[col_date], errors="coerce")

# ======================================================
# DASHBOARD TABS
# ======================================================

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📈 KPI Overview",
    "📊 Category Analysis",
    "📅 Time Trend",
    "🚨 Anomaly Detection",
    "📘 AI Governance Review"
])

# ======================================================
# TAB 1 – KPI
# ======================================================

with tab1:

    st.subheader("📈 Executive KPI Overview")

    if df[col_numeric].notna().sum() == 0:
        st.error("Selected numeric column contains no valid numeric data.")
    else:
        total_value = df[col_numeric].sum()
        avg_value = df[col_numeric].mean()
        max_value = df[col_numeric].max()

        c1, c2, c3 = st.columns(3)
        c1.metric("Total", f"{total_value:,.2f}")
        c2.metric("Average", f"{avg_value:,.2f}")
        c3.metric("Maximum", f"{max_value:,.2f}")

# ======================================================
# TAB 2 – CATEGORY
# ======================================================

with tab2:

    st.subheader("📊 Category Analysis")

    if col_category != "None":
        grouped = df.groupby(col_category)[col_numeric].sum().reset_index()

        fig = px.bar(
            grouped,
            x=col_category,
            y=col_numeric,
            color=col_numeric,
            template="plotly_white"
        )

        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No category column selected.")

# ======================================================
# TAB 3 – TIME TREND
# ======================================================

with tab3:

    st.subheader("📅 Time Trend Analysis")

    if col_date != "None":
        trend = df.groupby(col_date)[col_numeric].sum().reset_index()

        fig2 = px.line(
            trend,
            x=col_date,
            y=col_numeric,
            markers=True,
            template="plotly_white"
        )

        st.plotly_chart(fig2, use_container_width=True)
    else:
        st.info("No date column selected.")

# ======================================================
# TAB 4 – ANOMALY
# ======================================================

with tab4:

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

# ======================================================
# TAB 5 – AI GOVERNANCE
# ======================================================

with tab5:

    st.subheader("📘 AI Documentation Governance Review")

    doc_file = st.file_uploader(
        "Upload Documentation (PDF)",
        type=["pdf"],
        key="doc_upload"
    )

    if doc_file:

        text_data = []
        with pdfplumber.open(doc_file) as pdf:
            for page in pdf.pages:
                text_data.append(page.extract_text())

        full_text = "\n".join(text_data)

        st.text(full_text[:1000])

        st.markdown("### 🧠 AI Readiness Scoring")

        clarity = st.slider("Clarity (0-20)", 0, 20, 10)
        measurable = st.slider("Measurable KPIs (0-20)", 0, 20, 10)
        automation = st.slider("Automation Potential (0-20)", 0, 20, 10)
        ai_scope = st.slider("AI Integration Scope (0-20)", 0, 20, 10)
        business = st.slider("Business Impact Defined (0-20)", 0, 20, 10)

        total_score = clarity + measurable + automation + ai_scope + business

        st.metric("AI Readiness Score", f"{total_score} / 100")

        if total_score >= 80:
            st.success("Excellent AI-ready documentation.")
        elif total_score >= 60:
            st.warning("Moderate readiness. Improvement recommended.")
        else:
            st.error("Low AI readiness. Redesign required.")

st.success("✅ Enterprise Dashboard Active")