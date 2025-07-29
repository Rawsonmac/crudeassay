import pandas as pd
import plotly.graph_objects as go
from modules.optimizer import run_optimization

def run_sensitivity_analysis(assay_df, price_df, region, freight_cost):
    deltas = [-0.1, 0.1]  # -10% and +10%
    products = price_df["Product"].tolist()
    base = run_optimization(assay_df, price_df, region, freight_cost)["profit_per_bbl"]

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

    # Sort by absolute impact
    effects.sort(key=lambda x: abs(x[1]), reverse=True)

    return go.Figure(go.Bar(
        x=[x[1] for x in effects],
        y=[x[0] for x in effects],
        orientation='h'
    )).update_layout(title="Profit Sensitivity to Benchmark Price Changes")
