import streamlit as st
import polars as pl
import logging
from typing import List, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def detect_anomalies(df: pl.DataFrame, threshold: float = 2.0) -> pl.DataFrame:
    """Detects statistical anomalies in risk scores using Z-Score methodology.

    Args:
        df: Input Polars DataFrame containing risk data.
        threshold: Z-score threshold to classify an anomaly (default 2.0).

    Returns:
        pl.DataFrame: DataFrame containing only the anomalous records.
    """
    try:
        if df.is_empty() or "risk_score" not in df.columns:
            return pl.DataFrame()

        # Rule 6: Use lazy execution for potential scalability
        lf = df.lazy().with_columns([
            ((pl.col("risk_score") - pl.col("risk_score").mean()) /
             pl.col("risk_score").std()).alias("z_score")
        ]).filter(pl.col("z_score").abs() > threshold)

        return lf.collect()
    except Exception as e:
        logger.error(f"Anomaly detection failed: {e}")
        return pl.DataFrame()

def get_critical_suppliers(df: pl.DataFrame, risk_cutoff: float = 80.0) -> List[str]:
    """Identifies supplier names exceeding a specific critical risk threshold.

    Args:
        df: Input Polars DataFrame.
        risk_cutoff: The risk score above which a supplier is 'Critical'.

    Returns:
        List[str]: List of critical supplier names.
    """
    try:
        if df.is_empty() or "supplier_name" not in df.columns:
            return []

        critical_df = df.filter(pl.col("risk_score") >= risk_cutoff)
        return critical_df["supplier_name"].to_list()
    except Exception as e:
        logger.error(f"Failed to extract critical suppliers: {e}")
        return []

def render_alert_banner(critical_count: int, anomaly_count: int) -> None:
    """Renders high-visibility alert banners in the Streamlit UI.

    Args:
        critical_count: Number of suppliers in critical risk state.
        anomaly_count: Number of statistical anomalies detected.
    """
    try:
        if critical_count > 0:
            st.error(f"🚨 CRITICAL ALERT: {critical_count} Suppliers exceed risk thresholds!")

        if anomaly_count > 0:
            st.warning(f"⚠️ SYSTEM NOTICE: {anomaly_count} Statistical anomalies detected in stream.")

        if critical_count == 0 and anomaly_count == 0:
            st.success("✅ SYSTEM STATUS: Nominal. No immediate supply chain threats detected.")
    except Exception as e:
        logger.error(f"UI Banner rendering failed: {e}")

if __name__ == "__main__":
    # Smoke Test
    st.set_page_config(page_title="Alerts Component Test")

    # Mock Data
    test_data = pl.DataFrame({
        "supplier_name": ["GlobalLogistics", "TechParts", "AsiaExpress", "NordicFreight", "BioMed"],
        "risk_score": [15.0, 18.0, 85.0, 22.0, 95.0]
    })

    anomalies = detect_anomalies(test_data)
    criticals = get_critical_suppliers(test_data)

    st.write("### Alerts Component Smoke Test")
    render_alert_banner(len(criticals), len(anomalies))
    st.write("Data Sample:", test_data)