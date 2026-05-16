import polars as pl
import numpy as np
import logging
import streamlit as st
from typing import Dict, Any, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def simulate_disruption(
    base_data: pl.DataFrame,
    disruption_intensity: float,
    affected_regions: list[str]
) -> pl.DataFrame:
    """Simulates the impact of a disruption on global supplier risk scores.

    Args:
        base_data: Original Polars DataFrame containing supplier risk data.
        disruption_intensity: Multiplier for risk increase (1.0 to 5.0).
        affected_regions: List of strings representing regions under stress.

    Returns:
        pl.DataFrame: DataFrame with updated 'simulated_risk_score'.
    """
    try:
        if base_data.is_empty():
            return base_data

        # Rule 6: Use lazy execution for potential scalability
        lf = base_data.lazy().with_columns([
            pl.when(pl.col("region").is_in(affected_regions))
            .then(pl.col("risk_score") * disruption_intensity)
            .otherwise(pl.col("risk_score"))
            .clip(0, 100)
            .alias("simulated_risk_score")
        ])

        return lf.collect()
    except Exception as e:
        logger.error(f"Disruption simulation failed: {e}")
        st.warning("Could not complete disruption simulation.")
        return base_data

def calc_inventory_impact(
    current_inventory: float,
    daily_demand: float,
    lead_time_days: int
) -> Dict[str, float]:
    """Calculates stock-out risks based on current supply chain velocity.

    Args:
        current_inventory: Units currently in stock.
        daily_demand: Average units consumed per day.
        lead_time_days: Expected replenishment time in days.

    Returns:
        Dict[str, float]: Dictionary with 'days_cover' and 'shortfall_probability'.
    """
    try:
        days_cover = current_inventory / daily_demand if daily_demand > 0 else 999
        # Simplified probability: higher risk if lead time exceeds inventory cover
        shortfall_prob = np.clip((lead_time_days / (days_cover + 1e-9)) * 0.5, 0.0, 1.0)

        return {
            "days_cover": float(days_cover),
            "shortfall_probability": float(shortfall_prob)
        }
    except Exception as e:
        logger.error(f"Inventory impact calculation error: {e}")
        return {"days_cover": 0.0, "shortfall_probability": 1.0}

def project_lead_time_change(
    base_lead_time: float,
    port_congestion_index: float,
    labor_strike: bool
) -> float:
    """Projects future lead times using weighted disruption variables.

    Args:
        base_lead_time: Normal lead time in days.
        port_congestion_index: Scale of 1.0 to 2.0 (1.5 = 50% slower).
        labor_strike: Boolean flag indicating if a strike is active.

    Returns:
        float: Projected lead time in days.
    """
    try:
        strike_penalty = 1.4 if labor_strike else 1.0
        projected = base_lead_time * port_congestion_index * strike_penalty
        return float(round(projected, 2))
    except Exception as e:
        logger.error(f"Lead time projection error: {e}")
        return base_lead_time

if __name__ == "__main__":
    # Smoke Test
    print("Testing Scenario Simulator...")

    # Mock Data
    df = pl.DataFrame({
        "supplier": ["A", "B", "C"],
        "region": ["APAC", "EMEA", "APAC"],
        "risk_score": [20.0, 30.0, 15.0]
    })

    # Run simulation
    sim_df = simulate_disruption(df, 2.5, ["APAC"])
    print("Simulated Data (APAC Disruption x2.5):")
    print(sim_df)

    # Test Inventory Impact
    inv = calc_inventory_impact(1000, 100, 15)
    print(f"\nInventory Metrics: {inv}")

    # Test Lead Time Projection
    lt = project_lead_time_change(10, 1.3, True)
    print(f"Projected Lead Time (Congestion + Strike): {lt} days")