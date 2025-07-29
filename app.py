import streamlit as st
import pandas as pd
import os
from modules.optimizer import run_optimization
from modules.logistics import calculate_logistics_cost
from modules.utils import load_assay_file, load_benchmark_prices
import plotly.graph_objects as go

# --- Page Setup ---
st.set_page_config(page_title="Crude Slate Profit Optimizer", layout="wide")
st.title("🛢 Crude Slate Profit Optimizer")

# --- Sidebar: Assay Upload or Select Preset ---
st.sidebar.header("Crude Assay Input")
uploaded_file = st.sidebar.file_uploader("Upload your assay (CSV)", type="csv")
assay_files = sorted([
    f for f in os.listdir("data")
    if f.endswith(".csv") and f != "benchmark_prices.csv"
])
default_file = st.sidebar.selectbox("...or select a preset", assay_files)
assay_df = load_assay_file(uploaded_file, default_file)

# --- Sidebar: Region and Logistics ---
st.sidebar.header("Logistics Settings")
region = st.sidebar.selectbox("Target Market", ["Region_USGC", "Region_EU", "Region_Asia"])
include_logistics = st.sidebar.checkbox("Include Freight & Demurrage", value=True)
freight_cost = calculate_logistics_cost(region) if include_logistics else 0

# --- Sidebar: Pricing Input (keep all columns!) ---
st.sidebar.header("Benchmark Prices")
price_df = load_benchmark_prices()
price_df = st.sidebar.data_editor(price_df, key="price_editor")

# --- Run Optimization Automatically ---
try:
    result = run_optimization(assay_df, price_df, region, freight_cost)

    # --- Main Output ---
    st.subheader("📊 Optimized Product Slate")
    st.dataframe(result["slate"], use_container_width=True)
    st.metric("💰 Net Profit per Barrel", f"${result['profit_per_bbl']:.2f}")

    # --- Sensitivity Analysis ---
    st.subheader("📈 Sensitivity Analysis (±10% Price Shocks)")
    deltas = [-0.1, 0.1]
    products = price_df["Product"].tolist()
    base = result["profit_per_bbl"]
    effects = []

    for product in products:
        original_price = price_df.loc[price_df["Product"] == product, region].values[0]
        for d in deltas:
            modified = price_df.copy()
            modified.loc[modified["Product"] == product, region] = original_price * (1 + d)
            new_profit = run_optimization(assay_df, modified, region, freight_cost)["profit_per_bbl"]
            change = new_profit - base
            label = f"{product} {'+10%' if d > 0 else '-10%'}"
            effects.append((label, change))

    effects.sort(key=lambda x: abs(x[1]), reverse=True)
    labels, impacts = zip(*effects)

    fig = go.Figure(go.Bar(
        x=impacts,
        y=labels,
        orientation='h',
        marker=dict(color=['green' if v > 0 else 'red' for v in impacts]),
        hovertemplate="Impact: %{x:.2f} $/bbl<extra></extra>"
    ))

    fig.update_layout(
        title="💥 Sensitivity of Net Profit to Price Shocks",
        xaxis_title="Δ Profit ($/bbl)",
        yaxis_title="Benchmark Shock",
        template="plotly_white",
        margin=dict(l=120, r=20, t=60, b=40),
        height=500
    )

    st.plotly_chart(fig, use_container_width=True)

    # --- Optimization Summary & Reasoning ---
    st.subheader("🧠 Optimization Summary & Recommendation")

    slate_df = result["slate"]
    top_product = slate_df.sort_values("Profit ($)", ascending=False).iloc[0]
    top_name = top_product["Allocated Product"]
    top_profit = top_product["Profit ($)"]
    diesel_yield = slate_df[slate_df["Allocated Product"] == "Diesel"]["Volume"].values[0]
    resid_yield = slate_df[slate_df["Allocated Product"] == "Fuel Oil"]["Volume"].values[0]

    explanation = f"""
    - ✅ The most profitable product is **{top_name}**, generating **${top_profit:.2f}** per barrel of crude.
    - 🔍 **Diesel** makes up **{diesel_yield * 100:.1f}%** of this crude, and it's priced favorably in **{region}**, making it your top driver.
    - ⚠️ Resid (Fuel Oil) yield is **{resid_yield * 100:.1f}%** — consider blending or exporting if margins are weak.
    - 📦 Based on prices and logistics, this crude generates **${result['profit_per_bbl']:.2f} per barrel** overall in {region}.

    👉 You should direct processing/blending toward **{top_name}**, and seek regional arbitrage for any surplus diesel or jet fuel.
    """

    st.text_area("📋 Optimization Reasoning", explanation.strip(), height=280)

except ValueError as e:
    st.error(f"❌ Optimization failed: {e}")
