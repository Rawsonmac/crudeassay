import logging

def calculate_logistics_cost(region):
    """
    Calculate total logistics cost (freight + demurrage) for a given region.

    Args:
        region (str): Target market region (e.g., 'Region_USGC', 'Region_EU', 'Region_Asia').

    Returns:
        float: Total logistics cost in $/bbl.

    Raises:
        ValueError: If region is invalid or not found.
    """
    logistics_costs = {
        "Region_USGC": {"freight": 2.5, "demurrage": 0.5},
        "Region_EU": {"freight": 4.0, "demurrage": 1.0},
        "Region_Asia": {"freight": 5.5, "demurrage": 1.2}
    }

    if not isinstance(region, str):
        raise ValueError(f"Region must be a string, got {type(region)}")
    if region not in logistics_costs:
        raise ValueError(f"Invalid region: {region}. Must be one of {list(logistics_costs.keys())}")

    costs = logistics_costs[region]
    return costs["freight"] + costs["demurrage"]
