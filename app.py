import streamlit as st
import pandas as pd
from modules.optimizer import run_optimization
from modules.logistics import calculate_logistics_cost
from modules.sensitivity import run_sensitivity_analysis
from modules.utils import load_assay_file, load_benchmark_prices

# Cache data loading functions
@st.cache_data
def cached_load_assay_file(uploaded_file, default_file):
    return load_assay_file(uploaded_file, default_file)

@st.cache_data
def cached_load_benchmark_prices():
    return load_benchmark_prices()

# Set page config
st.set_page_config(page_title="Crude Slate Profit Optimizer", layout="wide", page_icon="🛢")
st.title("🛢 Crude Slate Profit Optimizer")

# Sidebar: Assay Selection
st.sidebar.header("Crude Assay")
uploaded_file = st.sidebar.file_uploader("Upload your assay (CSV)", type="csv")
default_file = st.sidebar.selectbox("...or select a preset", ["wti_light.csv", "banyu_urip.csv"])
try:
    assay_df = cached_load_assay_file(uploaded_file, default_file)
    st.sidebar.success(f"Loaded assay: {'Uploaded file' if uploaded_file else default_file}")
except Exception as e:
    st.sidebar.error(f"Error loading assay: {str(e)}")
    st.stop()

# Sidebar: Pricing Input
st.sidebar.header("Benchmark Prices")
try:
    price_df = cached_load_benchmark_prices()
    region = st.sidebar.selectbox("Target Market", ["Region_USGC", "Region_EU", "Region_Asia"])
    edited_prices = st.sidebar.data_editor(
        price_df[["Product", region]], num_rows="dynamic", key="price_editor"
    )
    # Update price_df with edited prices
    price_df[[region]] = edited_prices[region]
except Exception as e:
    st.sidebar.error(f"Error loading prices: {str(e)}")
    st.stop()

# Sidebar: Logistics Settings
st.sidebar.header("Logistics Settings")
include_logistics = st.sidebar.checkbox("Include Freight & Demurrage", value=True)

# Run Optimization
if st.sidebar.button("Run Optimization"):
    try:
        with st.spinner("Running optimization..."):
            freight_cost = calculate_logistics_cost(region) if include_logistics else 0
            result = run_optimization(assay_df, price_df, region, freight_cost)
        
        st.subheader("Optimized Product Slate")
        st.dataframe(result["slate"])
        st.metric("Net Profit per Barrel", f"${result['profit_per_bbl']:.2f}")

        st.subheader("Sensitivity Analysis")
        tornado = run_sensitivity_analysis(assay_df, price_df, region, freight_cost)
        st.plotly_chart(tornado, use_container_width=True)
    except Exception as e:
        st.error(f"Optimization failed: {str(e)}")
