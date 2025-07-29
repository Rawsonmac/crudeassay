import pandas as pd
import logging

def map_cut_to_product(cut):
    """Map a crude cut to a refined product."""
    CUT_TO_PRODUCT = {
        "naphtha": "Gasoline",
        "kero": "Jet/Kero",
        "kerosene": "Jet/Kero",
        "diesel": "Diesel",
        "resid": "Fuel Oil"
    }
    if not isinstance(cut, str):
        logging.warning(f"Invalid cut: {cut}, defaulting to Fuel Oil")
        return "Fuel Oil"
    cut = cut.lower()
    return CUT_TO_PRODUCT.get(cut, "Fuel Oil")

def run_optimization(assay_df, price_df, region, freight_cost, base_cost=50):
    """Optimize crude slate and calculate profit."""
    # Validate inputs
    required_assay_cols = ["Cut", "Volume"]
    required_price_cols = ["Product", region]
    if not all(col in assay_df.columns for col in required_assay_cols):
        raise ValueError("assay_df missing required columns: Cut, Volume")
    if not all(col in price_df.columns for col in required_price_cols):
        raise ValueError(f"price_df missing required columns: Product, {region}")
    if not pd.api.types.is_numeric_dtype(assay_df["Volume"]):
        raise ValueError("Volume column must be numeric")
    if assay_df.empty or price_df.empty:
        raise ValueError("Empty DataFrame provided")

    try:
        # Calculate total barrels
        total_bbl = assay_df["Volume"].sum()
        if total_bbl == 0:
            raise ValueError("Total volume is zero")

        # Map cuts to products
        assay_df["Allocated Product"] = assay_df["Cut"].apply(map_cut_to_product)

        # Merge with price_df
        slate = assay_df.merge(price_df[["Product", region]], left_on="Allocated Product", right_on="Product", how="left")
        slate[region] = slate[region].fillna(0)  # Handle missing prices
        slate["Product Price ($/bbl)"] = slate[region]
        slate["Profit ($)"] = (slate[region] - (base_cost + freight_cost)) * slate["Volume"]

        # Log unmatched products
        unmatched = slate[slate[region] == 0]["Allocated Product"].unique()
        if unmatched.size > 0:
            logging.warning(f"No prices found for products: {', '.join(unmatched)}")

        # Prepare output DataFrame
        slate = slate[["Cut", "Allocated Product", "Volume", "Product Price ($/bbl)", "Profit ($)"]]
        total_profit = slate["Profit ($)"].sum()
        profit_per_bbl = total_profit / total_bbl

        return {
            "slate": slate,
            "profit_per_bbl": profit_per_bbl
        }
    except Exception as e:
        raise ValueError(f"Optimization failed: {str(e)}")import pandas as pd
import logging

def map_cut_to_product(cut):
    """Map a crude cut to a refined product."""
    CUT_TO_PRODUCT = {
        "naphtha": "Gasoline",
        "kero": "Jet/Kero",
        "kerosene": "Jet/Kero",
        "diesel": "Diesel",
        "resid": "Fuel Oil"
    }
    if not isinstance(cut, str):
        logging.warning(f"Invalid cut: {cut}, defaulting to Fuel Oil")
        return "Fuel Oil"
    cut = cut.lower()
    return CUT_TO_PRODUCT.get(cut, "Fuel Oil")

def run_optimization(assay_df, price_df, region, freight_cost, base_cost=50):
    """Optimize crude slate and calculate profit."""
    # Validate inputs
    required_assay_cols = ["Cut", "Volume"]
    required_price_cols = ["Product", region]
    if not all(col in assay_df.columns for col in required_assay_cols):
        raise ValueError("assay_df missing required columns: Cut, Volume")
    if not all(col in price_df.columns for col in required_price_cols):
        raise ValueError(f"price_df missing required columns: Product, {region}")
    if not pd.api.types.is_numeric_dtype(assay_df["Volume"]):
        raise ValueError("Volume column must be numeric")
    if assay_df.empty or price_df.empty:
        raise ValueError("Empty DataFrame provided")

    try:
        # Calculate total barrels
        total_bbl = assay_df["Volume"].sum()
        if total_bbl == 0:
            raise ValueError("Total volume is zero")

        # Map cuts to products
        assay_df["Allocated Product"] = assay_df["Cut"].apply(map_cut_to_product)

        # Merge with price_df
        slate = assay_df.merge(price_df[["Product", region]], left_on="Allocated Product", right_on="Product", how="left")
        slate[region] = slate[region].fillna(0)  # Handle missing prices
        slate["Product Price ($/bbl)"] = slate[region]
        slate["Profit ($)"] = (slate[region] - (base_cost + freight_cost)) * slate["Volume"]

        # Log unmatched products
        unmatched = slate[slate[region] == 0]["Allocated Product"].unique()
        if unmatched.size > 0:
            logging.warning(f"No prices found for products: {', '.join(unmatched)}")

        # Prepare output DataFrame
        slate = slate[["Cut", "Allocated Product", "Volume", "Product Price ($/bbl)", "Profit ($)"]]
        total_profit = slate["Profit ($)"].sum()
        profit_per_bbl = total_profit / total_bbl

        return {
            "slate": slate,
            "profit_per_bbl": profit_per_bbl
        }
    except Exception as e:
        raise ValueError(f"Optimization failed: {str(e)}")
