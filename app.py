import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
import pdfplumber
import re

# ======================================================
# PAGE CONFIG
# ======================================================

st.set_page_config(
    page_title="Enterprise AI Governance Platform",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ======================================================
# STYLING
# ======================================================

st.markdown("""
<style>
.main {background-color: #f4f6f9;}
h1 {color: #111827;}
h2 {color: #1f2937;}
.stMetric {background-color: white; padding: 15px; border-radius: 10px;}
</style>
""", unsafe_allow_html=True)

# ======================================================
# HEADER
# ======================================================

st.title("🚀 Enterprise AI Transformation Control Platform")
st.caption("Data Intelligence • AI Governance • Executive Control")

# ======================================================
# SIDEBAR DATA UPLOAD
# ======================================================

st.sidebar.header("📂 Data Upload")

uploaded_file = st.sidebar.file_uploader(
    "Upload Excel / CSV",
    type=["xlsx", "csv"]
)

def load_data(file):
    if file.name.endswith(".csv"):
        return pd.read_csv(file)
    else:
        excel = pd.ExcelFile(file)
        sheet = st.sidebar.selectbox("Select Sheet", excel.sheet_names)
        return pd.read_excel(file, sheet_name=sheet)

if uploaded_file is None:
    st.info("👈 Upload dataset to begin.")
    st.stop()

df = load_data(uploaded_file)
st.subheader("🔍 Data Preview")
st.dataframe(df, use_container_width=True)

columns = df.columns.tolist()

# ======================================================
# MAPPING
# ======================================================

st.subheader("🧭 Column Mapping")

with st.form("mapping_form"):
    col_numeric = st.selectbox("Numeric Column (Required)", ["None"] + columns)
    col_category = st.selectbox("Category Column (Optional)", ["None"] + columns)
    submit = st.form_submit_button("Apply Mapping")

if not submit or col_numeric == "None":
    st.warning("Select numeric column to continue.")
    st.stop()

df[col_numeric] = (
    df[col_numeric]
    .astype(str)
    .str.replace(",", "", regex=False)
    .str.replace("₹", "", regex=False)
    .str.replace("$", "", regex=False)
)
df[col_numeric] = pd.to_numeric(df[col_numeric], errors="coerce")

# ======================================================
# TABS
# ======================================================

tab1, tab2, tab3 = st.tabs([
    "📊 Data Dashboard",
    "🚨 Anomaly Detection",
    "📘 AI Governance Intelligence"
])

# ======================================================
# TAB 1 – DASHBOARD
# ======================================================

with tab1:

    total = df[col_numeric].sum()
    avg = df[col_numeric].mean()
    max_val = df[col_numeric].max()

    c1, c2, c3 = st.columns(3)
    c1.metric("Total", f"{total:,.2f}")
    c2.metric("Average", f"{avg:,.2f}")
    c3.metric("Maximum", f"{max_val:,.2f}")

    if col_category != "None":
        grouped = df.groupby(col_category)[col_numeric].sum().reset_index()
        fig = px.bar(grouped, x=col_category, y=col_numeric, template="plotly_white")
        st.plotly_chart(fig, use_container_width=True)

# ======================================================
# TAB 2 – ANOMALY
# ======================================================

with tab2:

    std_dev = df[col_numeric].std()

    if std_dev and std_dev != 0:
        df["Z_Score"] = (df[col_numeric] - df[col_numeric].mean()) / std_dev
        anomalies = df[np.abs(df["Z_Score"]) > 3]
        st.metric("Anomaly Count", len(anomalies))
        if len(anomalies) > 0:
            st.dataframe(anomalies)
    else:
        st.info("Not enough variance.")

# ======================================================
# TAB 3 – AI GOVERNANCE INTELLIGENCE
# ======================================================

with tab3:

    st.subheader("📘 Upload Documentation for AI Governance Review")

    doc_file = st.file_uploader("Upload PDF Document", type=["pdf"])

    if doc_file:

        text_data = []
        with pdfplumber.open(doc_file) as pdf:
            for page in pdf.pages:
                text_data.append(page.extract_text())

        full_text = "\n".join(text_data).lower()

        st.subheader("📄 Document Preview")
        st.text(full_text[:1200])

        # ==================================================
        # AI EXECUTIVE SUMMARY
        # ==================================================

        st.markdown("### 🤖 AI Executive Summary")

        sentences = re.split(r'\.|\n', full_text)
        keywords = ["ai", "risk", "automation", "kpi", "revenue", "control", "compliance"]
        important = [s.strip() for s in sentences if any(k in s for k in keywords)]
        summary = ". ".join(important[:5])

        if summary:
            st.success(summary)
        else:
            st.info("No AI-relevant insights detected.")

        # ==================================================
        # AI SENTIMENT ANALYSIS
        # ==================================================

        st.markdown("### 🧠 Sentiment Analysis")

        positive_words = ["improve", "optimize", "enhance", "increase", "efficient"]
        negative_words = ["risk", "delay", "issue", "failure", "weak"]

        pos_count = sum(full_text.count(word) for word in positive_words)
        neg_count = sum(full_text.count(word) for word in negative_words)

        if pos_count > neg_count:
            sentiment = "Positive / Growth-Oriented"
        elif neg_count > pos_count:
            sentiment = "Risk-Focused / Defensive"
        else:
            sentiment = "Neutral"

        st.metric("Document Sentiment", sentiment)

        # ==================================================
        # MISSING KPI DETECTOR
        # ==================================================

        st.markdown("### 📊 Missing KPI Detector")

        if "kpi" not in full_text:
            st.error("No KPI definitions found.")
        else:
            st.success("KPI references detected.")

        if "%" not in full_text:
            st.warning("No measurable targets (%) found.")
        else:
            st.success("Measurable targets detected.")

        # ==================================================
        # RISK COVERAGE SCORE
        # ==================================================

        st.markdown("### 🚨 Risk Coverage Score")

        risk_keywords = ["risk", "fraud", "control", "audit", "compliance"]
        risk_score = sum(full_text.count(word) for word in risk_keywords)

        risk_coverage = min(risk_score * 5, 100)

        st.metric("Risk Coverage Score", f"{risk_coverage}/100")

        # ==================================================
        # AI MATURITY CLASSIFICATION
        # ==================================================

        st.markdown("### 🏆 AI Maturity Classification")

        ai_terms = ["predictive", "automation", "machine learning", "anomaly", "ai model"]
        ai_score = sum(full_text.count(word) for word in ai_terms)

        if ai_score > 10:
            maturity = "Advanced AI-Driven"
        elif ai_score > 4:
            maturity = "Intermediate AI-Enabled"
        else:
            maturity = "Basic Rule-Based"

        st.success(f"AI Maturity Level: {maturity}")

st.success("✅ Enterprise AI Governance Platform Active")