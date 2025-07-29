import pandas as pd
import os
import streamlit as st

@st.cache_data
def load_assay_file(uploaded_file, default_file):
    """
    Load crude assay data from an uploaded file or a default CSV file.

    Args:
        uploaded_file (streamlit.UploadedFile or None): Uploaded CSV file from Streamlit.
        default_file (str): Name of the default CSV file (e.g., 'wti_light.csv').

    Returns:
        pandas.DataFrame: DataFrame with assay data (columns: Cut, Volume).

    Raises:
        ValueError: If inputs are invalid or required columns are missing.
        FileNotFoundError: If the default file is not found.
    """
    required_cols = ["Cut", "Volume"]
    data_dir = os.getenv("DATA_DIR", "data")

    try:
        if uploaded_file:
            df = pd.read_csv(uploaded_file)
        else:
            if not isinstance(default_file, str):
                raise ValueError(f"Default file must be a string, got {type(default_file)}")
            file_path = os.path.join(data_dir, default_file)
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"Default file not found: {file_path}")
            df = pd.read_csv(file_path)

        if not all(col in df.columns for col in required_cols):
            raise ValueError(f"Assay file missing required columns: {required_cols}")
        if not pd.api.types.is_numeric_dtype(df["Volume"]):
            raise ValueError("Volume column must be numeric")
        
        return df
    except Exception as e:
        raise ValueError(f"Failed to load assay file: {str(e)}")

@st.cache_data
def load_benchmark_prices(file_path=None):
    """
    Load benchmark price data from a CSV file.

    Args:
        file_path (str, optional): Path to the benchmark prices CSV file. 
            Defaults to 'data/benchmark_prices.csv'.

    Returns:
        pandas.DataFrame: DataFrame with columns Product, Region_USGC, Region_EU, Region_Asia.

    Raises:
        FileNotFoundError: If the benchmark prices file is not found.
        ValueError: If the file is invalid or missing required columns.
    """
    default_path = file_path or os.getenv("BENCHMARK_PRICES", "data/benchmark_prices.csv")
    required_cols = ["Product", "Region_USGC", "Region_EU", "Region_Asia"]

    try:
        if not os.path.exists(default_path):
            raise FileNotFoundError(f"Benchmark prices file not found: {default_path}")
        df = pd.read_csv(default_path)

        if not all(col in df.columns for col in required_cols):
            raise ValueError(f"Benchmark prices file missing required columns: {required_cols}")
        for col in required_cols[1:]:
            if not pd.api.types.is_numeric_dtype(df[col]):
                raise ValueError(f"Column {col} must be numeric")
        
        return df
    except Exception as e:
        raise ValueError(f"Failed to read benchmark prices: {str(e)}")
