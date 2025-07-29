import streamlit as st
import pandas as pd
import os
from modules.optimizer import run_optimization
from modules.logistics import calculate_logistics_cost
from modules.sensitivity import run_sensitivity_analysis
from modules.utils import load_assay_file, load_benchmark_prices

st.set_page_config(page_title="Crude Slate Profit Optimizer", layout="wide")
st.title("🛢 Crude Slate Profit Optimizer")

# Confirm app loaded
st.write("App loaded ✅")

# Get all assay files from data folder
assay_files = sorted([
    f for f in os.listdir("data") 
    if f.endswith(".csv") and f != "benchmark_prices.csv"
])

# Crude assay selection
st.sidebar.header("Crude Assay")
uploaded_file = st.sidebar.file_uploader("Upload your assay (CSV)", type="csv")
default_file = st.sidebar.selectbox("...or select a preset", assay_files)
assay_df = load_assay_file(uploaded_file, default_file)

# Pricing Input
st.sidebar.header("Benchmark Prices (editable)")
price_df = load_benchmark_prices()
edited_prices = st.sidebar.data_editor(price_df[["Product", "Region_USGC"]])

# Logistics
st.sidebar.header("Logistics")
region = st.sidebar.selectbox("Target Market", ["Region_USGC", "Region_EU", "Region_Asia"])
include_logistics = st.sidebar.checkbox("Include Freight & Demurrage", value=True)

# Run optimization
if st.sidebar.button("Run Optimization"):
    freight_cost = calculate_logistics_cost(region) if include_logistics else 0
    result = run_optimization(assay_df, price_df, region, freight_cost)

    st.subheader("Optimized Product Slate")
    st.dataframe(result["slate"])

    st.metric("Net Profit per Barrel", f"${result['profit_per_bbl']:.2f}")

    st.subheader("Sensitivity Analysis")
    fig = run_sensitivity_analysis(assay_df, price_df, region, freight_cost)
    st.plotly_chart(fig, use_container_width=True)
