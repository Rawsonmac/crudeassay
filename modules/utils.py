import pandas as pd

def load_assay_file(uploaded_file, default_file):
    """Load assay data from uploaded file or default file."""
    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
    elif default_file is not None:
        df = pd.read_csv(f"data/{default_file}")
    else:
        raise ValueError("No assay file provided or found")
    df.columns = df.columns.str.strip()  # Remove whitespace
    required_cols = ["Cut", "Volume"]
    if not all(col in df.columns for col in required_cols):
        raise ValueError(f"assay_df missing required columns: {required_cols}. Found: {df.columns.tolist()}")
    return df

def load_benchmark_prices():
    """Load benchmark prices from CSV."""
    try:
        df = pd.read_csv("data/benchmark_prices.csv")
        df.columns = df.columns.str.strip()  # Remove whitespace
        expected_cols = ["Product", "Region_USGC", "Region_EU", "Region_Asia"]
        if not all(col in df.columns for col in expected_cols):
            raise ValueError(f"benchmark_prices.csv missing required columns: {expected_cols}. Found: {df.columns.tolist()}")
        return df
    except FileNotFoundError:
        raise ValueError("benchmark_prices.csv not found in data directory")
    except Exception as e:
        raise ValueError(f"Failed to load benchmark_prices.csv: {str(e)}")
