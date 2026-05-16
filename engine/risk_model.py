import polars as pl
import numpy as np
import logging
import streamlit as st
from typing import Dict, Any, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def normalize_scores(scores: np.ndarray) -> np.ndarray:
    """Normalizes an array of scores to a 0-100 scale using Min-Max scaling.

    Args:
        scores: A numpy array of raw risk components.

    Returns:
        np.ndarray: Normalized scores. Returns zeros if input is invalid.
    """
    try:
        min_val = np.min(scores)
        max_val = np.max(scores)
        if max_val == min_val:
            return np.zeros_like(scores)
        return (scores - min_val) / (max_val - min_val) * 100
    except Exception as e:
        logger.error(f"Normalization error: {e}")
        return np.zeros_like(scores)

def score_geo_risk(region_impact: float, event_density: int) -> float:
    """Calculates geographical risk based on event density and impact factors.

    Args:
        region_impact: Coefficient representing regional sensitivity (0.0 - 1.0).
        event_density: Count of disruptive events in the vicinity.

    Returns:
        float: Computed geo risk score.
    """
    try:
        # Logistic growth curve simulation for event density
        return float(100 / (1 + np.exp(-0.5 * (event_density - 5))) * region_impact)
    except Exception as e:
        logger.error(f"Geo risk scoring error: {e}")
        return 0.0

def score_delay_risk(lead_time_days: int, variance: float) -> float:
    """Computes risk of delivery delay using lead time volatility.

    Args:
        lead_time_days: Current average lead time.
        variance: Standard deviation or variance of historical lead times.

    Returns:
        float: Computed delay risk score.
    """
    try:
        raw_score = (lead_time_days * 0.4) + (variance * 0.6)
        return float(np.clip(raw_score, 0, 100))
    except Exception as e:
        logger.error(f"Delay risk scoring error: {e}")
        return 0.0

def score_financial_risk(revenue_at_risk: float, supplier_rating: float) -> float:
    """Evaluates financial exposure based on revenue and supplier health.

    Args:
        revenue_at_risk: Dollar value exposed to this supplier.
        supplier_rating: Health score of the supplier (0.0 to 1.0, where 1.0 is healthy).

    Returns:
        float: Computed financial risk score.
    """
    try:
        health_penalty = (1 - supplier_rating) * 100
        exposure_factor = np.log1p(revenue_at_risk) / 20 # Normalized log scale
        return float(np.clip((health_penalty * 0.7) + (exposure_factor * 30), 0, 100))
    except Exception as e:
        logger.error(f"Financial risk scoring error: {e}")
        return 0.0

def compute_risk_score(data: pl.DataFrame) -> pl.DataFrame:
    """Primary engine function to aggregate risk components into a master score.

    Args:
        data: Polars DataFrame containing geo, delay, and financial metrics.

    Returns:
        pl.DataFrame: DataFrame with added 'total_risk_score' column.
    """
    try:
        if data.is_empty():
            return data

        # Rule 6: Use lazy execution for potential scalability
        lf = data.lazy().with_columns([
            ((pl.col("geo_risk") * 0.4) +
             (pl.col("delay_risk") * 0.3) +
             (pl.col("financial_risk") * 0.3)).alias("total_risk_score")
        ])

        return lf.collect()
    except Exception as e:
        logger.error(f"Compute risk score error: {e}")
        st.warning("Risk engine calculation failed for one or more records.")
        return data

if __name__ == "__main__":
    # Smoke Test
    print("Testing Risk Model Logic...")

    # Generate dummy data
    df = pl.DataFrame({
        "supplier": ["S1", "S2", "S3"],
        "geo_risk": [10.0, 80.0, 45.0],
        "delay_risk": [20.0, 75.0, 30.0],
        "financial_risk": [5.0, 90.0, 50.0]
    })

    results = compute_risk_score(df)
    print(results)

    # Test normalization
    raw = np.array([10, 20, 30, 40, 50])
    normed = normalize_scores(raw)
    print(f"Normalized Array: {normed}")