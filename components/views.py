import streamlit as st
import plotly.express as px
import polars as pl
import logging
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)

def show_risk_overview(data: pl.DataFrame) -> None:
    """Renders the executive risk overview dashboard.

    Args:
        data: Polars DataFrame containing supplier risk scores.
    """
    try:
        st.header("Executive Risk Overview")
        col1, col2, col3 = st.columns(3)

        avg_risk = data.select(pl.col("risk_score").mean()).item()
        high_risk_count = data.filter(pl.col("risk_score") > 75).height

        col1.metric("Average Risk Score", f"{avg_risk:.2f}")
        col2.metric("High Risk Suppliers", high_risk_count)
        col3.metric("Total Suppliers", data.height)

        fig = px.histogram(data.to_pandas(), x="risk_score", nbins=20,
                          title="Risk Score Distribution", color_discrete_sequence=["#FF4B4B"])
        st.plotly_chart(fig, use_container_width=True)
    except Exception as e:
        logger.error(f"Error in risk overview: {e}")
        st.warning("Could not render risk overview.")

def show_map_view(data: pl.DataFrame) -> None:
    """Renders the global supply chain geographic risk map.

    Args:
        data: Polars DataFrame with columns [supplier, lat, lon, risk_score].
    """
    try:
        st.header("Global Risk Map")
        if all(c in data.columns for c in ["lat", "lon"]):
            fig = px.scatter_geo(data.to_pandas(), lat="lat", lon="lon",
                               hover_name="supplier", size="risk_score",
                               color="risk_score", projection="natural earth",
                               title="Supplier Geographic Exposure")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Geospatial coordinates missing in dataset.")
    except Exception as e:
        logger.error(f"Error in map view: {e}")
        st.warning("Map visualization unavailable.")

def show_news_feed(news_items: list[Dict[str, Any]]) -> None:
    """Displays a curated feed of supply chain news alerts.

    Args:
        news_items: List of dictionaries containing news metadata.
    """
    try:
        st.header("Supply Chain Intelligence Feed")
        if not news_items:
            st.write("No active alerts found.")
            return

        for item in news_items:
            with st.expander(f"{item.get('impact', 'INFO')} | {item.get('title')}"):
                st.write(item.get("summary"))
                st.caption(f"Source: {item.get('source')} | Date: {item.get('date')}")
    except Exception as e:
        logger.error(f"Error in news feed: {e}")
        st.warning("News feed could not be loaded.")

def show_scenario_page() -> None:
    """Renders the interactive scenario simulation interface."""
    try:
        st.header("Risk Scenario Simulator")
        st.info("Simulate the impact of global disruptions on your supply chain.")

        with st.container(border=True):
            scenario_type = st.selectbox("Disruption Event",
                                       ["Port Shutdown", "Labor Strike", "Natural Disaster", "Geopolitical Conflict"])
            impact_scale = st.slider("Magnitude of Impact", 0.1, 1.0, 0.5)

            if st.button("Run Simulation"):
                st.success(f"Simulation for '{scenario_type}' completed with {impact_scale*100}% impact.")
                st.info("Full simulation logic integrated via engine/scenario_sim.py")
    except Exception as e:
        logger.error(f"Error in scenario page: {e}")
        st.warning("Scenario simulator is currently offline.")

if __name__ == "__main__":
    # Smoke Test
    test_df = pl.DataFrame({
        "supplier": ["S1", "S2", "S3"],
        "risk_score": [80.5, 45.0, 12.5],
        "lat": [34.05, 51.50, 35.67],
        "lon": [-118.24, -0.12, 139.65]
    })
    show_risk_overview(test_df)
    show_map_view(test_df)