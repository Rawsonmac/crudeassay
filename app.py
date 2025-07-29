import streamlit as st
import pandas as pd
import os
try:
    from modules.optimizer import run_optimization
    from modules.logistics import calculate_logistics_cost
    from modules.sensitivity import run_sensitivity_analysis
    from modules.utils import load_assay_file, load_benchmark_prices
except ImportError as e:
    st.error(f"Failed to import modules: {str(e)}")
    st.stop()

# Set page config
st.set_page_config(page_title="Crude Slate Profit Optimizer", layout="wide", page_icon="🛢")
st.title("🛢 Crude Slate Profit Optimizer")

# Get assay files
data_dir = os.getenv("DATA_DIR", "data")
try:
    if not os.path.exists(data_dir):
        st.error(f"Data directory not found: {data_dir}")
        st.stop()
    assay_files = sorted([f for f in os.listdir(data_dir) if f.endswith(".csv") and f != "benchmark_prices.csv"])
    if not assay_files:
        st.error("No assay files found in data directory")
        st.stop()
except Exception as e:
    st.error(f"Error accessing data directory: {str(e)}")
    st.stop()

# Assay Selection
st.sidebar.header("Crude Assay")
st.sidebar.download_button(
    label="Download sample assay CSV",
    data=pd.DataFrame({"Cut": ["Naphtha", "Kero"], "Volume": [1000, 2000]}).to_csv(index=False),
    file_name="sample_assay.csv",
    mime="text/csv"
)
uploaded_file = st.sidebar.file_uploader("Upload your assay (CSV)", type="csv")
default_file = st.sidebar.selectbox("...or select a preset", assay_files)
try:
    assay_df = load_assay_file(uploaded_file, default_file)
    st.sidebar.success(f"Loaded assay: {'Uploaded file' if uploaded_file else default_file}")
except Exception as e:
    st.sidebar.error(f"Error loading assay: {str(e)}")
    st.stop()

# Pricing Input
st.sidebar.header("Benchmark Prices")
try:
    price_df = load_benchmark_prices()
    region = st.sidebar.selectbox("Target Market", ["Region_USGC", "Region_EU", "Region_Asia"])
    if region not in price_df.columns:
        st.error(f"Region {region} not found in benchmark prices")
        st.stop()
    edited_prices = st.sidebar.data_editor(price_df[["Product", region]], num_rows="dynamic")
    if (edited_prices[region] < 0).any():
        st.error("Prices cannot be negative")
        st.stop()
    price_df[region] = edited_prices[region]
except Exception as e:
    st.sidebar.error(f"Error loading prices: {str(e)}")
    st.stop()

# Logistics Settings
st.sidebar.header("Logistics Settings")
include_logistics = st.sidebar.checkbox("Include Freight & Demurrage", value=True)

# Run Optimization
if st.sidebar.button("Run Optimization"):
    try:
        with st.spinner("Running optimization..."):
            freight_cost = calculate_logistics_cost(region) if include_logistics else 0
            result = run_optimization(assay_df, price_df, region, freight_cost)
            if not isinstance(result, dict) or "slate" not in result or "profit_per_bbl" not in result:
                st.error("Invalid optimization result")
                st.stop()
            
            st.subheader("Optimized Product Slate")
            st.dataframe(result["slate"])
            st.metric("Net Profit per Barrel", f"${result['profit_per_bbl']:.2f}")

            st.subheader("Sensitivity Analysis")
            tornado = run_sensitivity_analysis(assay_df, price_df, region, freight_cost)
            st.plotly_chart(tornado, use_container_width=True)
    except Exception as e:
        st.error(f"Optimization failed: {str(e)}")
