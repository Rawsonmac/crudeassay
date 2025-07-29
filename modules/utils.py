import pandas as pd

def load_assay_file(uploaded_file, default_file):
    """Loads an uploaded or preset assay CSV."""
    if uploaded_file:
        return pd.read_csv(uploaded_file)
    else:
        return pd.read_csv(f"data/{default_file}")

def load_benchmark_prices():
    """Loads the benchmark pricing table."""
    return pd.read_csv("data/benchmark_prices.csv")
