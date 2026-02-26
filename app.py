import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Transformation Control Dashboard", layout="wide")

st.title("🚀 Transformation Control Dashboard")

# ---------------------------------------------------
# 📂 IMPORT SECTION
# ---------------------------------------------------

st.sidebar.header("📂 Data Import")

uploaded_file = st.sidebar.file_uploader(
    "Upload Transformation Excel File",
    type=["xlsx"]
)

def load_data_from_file(file):
    try:
        modules = pd.read_excel(file, sheet_name="Modules_Tracking")
        api = pd.read_excel(file, sheet_name="API_Metrics")
        ai = pd.read_excel(file, sheet_name="AI_Performance")
        reports = pd.read_excel(file, sheet_name="Reporting_Adoption")
        revenue = pd.read_excel(file, sheet_name="Revenue_Model")
        risk = pd.read_excel(file, sheet_name="Risk_Register")
        return modules, api, ai, reports, revenue, risk
    except Exception as e:
        st.error(f"Error loading file: {e}")
        st.stop()

# If file uploaded use it, else load default
if uploaded_file:
    modules, api, ai, reports, revenue, risk = load_data_from_file(uploaded_file)
    st.sidebar.success("Custom file loaded successfully.")
else:
    try:
        modules, api, ai, reports, revenue, risk = load_data_from_file("Transformation_Data.xlsx")
        st.sidebar.info("Using default local file.")
    except:
        st.warning("Upload Excel file to begin.")
        st.stop()

# ---------------------------------------------------
# 1️⃣ TECHNICAL HEALTH
# ---------------------------------------------------
st.header("1️⃣ Technical Health")

total_modules = len(modules)
migrated_modules = len(modules[modules["Status"] == "Migrated"])
pending_modules = total_modules - migrated_modules

col1, col2, col3 = st.columns(3)
col1.metric("Total Modules", total_modules)
col2.metric("Migrated", migrated_modules)
col3.metric("Pending", pending_modules)

if total_modules > 0:
    st.progress(migrated_modules / total_modules)

# ---------------------------------------------------
# 2️⃣ API PERFORMANCE
# ---------------------------------------------------
st.header("2️⃣ Integration Performance")

total_apis = len(api)
documented_percent = (api["Documented"] == "Yes").mean() * 100 if total_apis else 0
auth_percent = (api["Auth_Enabled"] == "Yes").mean() * 100 if total_apis else 0
avg_response = api["Avg_Response_Time_ms"].mean() if total_apis else 0
error_rate = api["Error_Rate_%"].mean() if total_apis else 0

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total APIs", total_apis)
col2.metric("Documented %", f"{documented_percent:.1f}%")
col3.metric("Auth Enabled %", f"{auth_percent:.1f}%")
col4.metric("Avg Response (ms)", f"{avg_response:.0f}")

st.metric("Avg Error Rate %", f"{error_rate:.2f}")

# ---------------------------------------------------
# 3️⃣ AI PERFORMANCE
# ---------------------------------------------------
st.header("3️⃣ AI Performance")

live_models = len(ai[ai["Model_Status"] == "Live"])
avg_accuracy = ai["Accuracy_%"].mean() if len(ai) else 0
avg_inference = ai["Inference_Time_ms"].mean() if len(ai) else 0
avg_impact = ai["Business_Impact_%"].mean() if len(ai) else 0

col1, col2, col3, col4 = st.columns(4)
col1.metric("Live Models", live_models)
col2.metric("Avg Accuracy %", f"{avg_accuracy:.1f}")
col3.metric("Avg Inference (ms)", f"{avg_inference:.0f}")
col4.metric("Business Impact %", f"{avg_impact:.1f}")

# ---------------------------------------------------
# 4️⃣ REPORTING VISIBILITY
# ---------------------------------------------------
st.header("4️⃣ Reporting & Adoption")

migrated_reports = len(reports[reports["Migrated"] == "Yes"])
adoption_avg = reports["Adoption_%"].mean() if len(reports) else 0

col1, col2 = st.columns(2)
col1.metric("Reports Migrated", migrated_reports)
col2.metric("Avg User Adoption %", f"{adoption_avg:.1f}")

# ---------------------------------------------------
# 5️⃣ REVENUE ALIGNMENT
# ---------------------------------------------------
st.header("5️⃣ Revenue Alignment")

total_revenue = revenue["Projected_Revenue"].sum() if len(revenue) else 0
total_cost_saving = revenue["Annual_Cost_Saving"].sum() if len(revenue) else 0

col1, col2 = st.columns(2)
col1.metric("Projected Revenue", f"₹ {total_revenue:,.0f}")
col2.metric("Annual Cost Saving", f"₹ {total_cost_saving:,.0f}")

if len(revenue):
    fig = px.bar(revenue, x="Module_Name", y="Projected_Revenue",
                 title="Revenue by Module")
    st.plotly_chart(fig, use_container_width=True)

# ---------------------------------------------------
# 6️⃣ RISK MANAGEMENT
# ---------------------------------------------------
st.header("6️⃣ Risk Management")

if len(risk):
    risk["Calculated_Risk"] = risk["Impact_Score_1_10"] * risk["Probability_1_10"]
    high_risk = len(risk[risk["Calculated_Risk"] > 50])
    st.metric("High Risk Items", high_risk)

    fig2 = px.bar(risk, x="Risk_Category", y="Calculated_Risk",
                  color="Calculated_Risk",
                  title="Risk Exposure by Category")
    st.plotly_chart(fig2, use_container_width=True)

st.success("✅ Dashboard is Live & Connected")