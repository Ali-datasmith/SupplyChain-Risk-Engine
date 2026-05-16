import plotly.graph_objects as go
import plotly.express as px
import polars as pl
import streamlit as st
import logging
from typing import Dict, Any, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def build_scatter_geo(df: pl.DataFrame, layout_config: Dict[str, Any]) -> go.Figure:
    """Builds a scatter geographic map showing supplier locations and risk levels.

    Args:
        df: Polars DataFrame containing 'lat', 'lon', 'risk_score', and 'supplier_name'.
        layout_config: Dictionary containing Plotly layout overrides (from theme.py).

    Returns:
        go.Figure: A Plotly Figure object.
    """
    try:
        if df.is_empty():
            return go.Figure()

        fig = px.scatter_geo(
            df.to_pandas(),  # Plotly express still has better interop with Pandas for geo
            lat="lat",
            lon="lon",
            hover_name="supplier_name",
            size="risk_score",
            color="risk_score",
            color_continuous_scale="RdYlGn_r",
            projection="natural earth"
        )

        fig.update_layout(**layout_config)
        return fig
    except Exception as e:
        logger.error(f"Failed to build scatter geo map: {e}")
        st.warning("Map visualization failed to render.")
        return go.Figure()

def build_choropleth(df: pl.DataFrame, layout_config: Dict[str, Any]) -> go.Figure:
    """Creates a choropleth map aggregating risk by country/region.

    Args:
        df: Polars DataFrame with 'iso_alpha' and 'avg_risk'.
        layout_config: Dictionary for styling.

    Returns:
        go.Figure: Plotly choropleth figure.
    """
    try:
        fig = px.choropleth(
            df.to_pandas(),
            locations="iso_alpha",
            color="avg_risk",
            hover_name="country",
            color_continuous_scale="OrRd"
        )
        fig.update_layout(**layout_config)
        return fig
    except Exception as e:
        logger.error(f"Choropleth error: {e}")
        return go.Figure()

def add_risk_zones(fig: go.Figure, zones: pl.DataFrame) -> go.Figure:
    """Overlays circular risk impact zones (e.g., hurricane radius) onto an existing map.

    Args:
        fig: The base Plotly figure.
        zones: DataFrame with 'lat', 'lon', and 'radius_km'.

    Returns:
        go.Figure: The modified Plotly figure.
    """
    try:
        for row in zones.iter_rows(named=True):
            fig.add_trace(go.Scattergeo(
                lat=[row['lat']],
                lon=[row['lon']],
                mode="markers",
                marker=dict(
                    size=row['radius_km'] / 10,  # Scaled for visualization
                    color="rgba(255, 0, 0, 0.3)",
                    line=dict(width=2, color="Red")
                ),
                name=f"Risk Zone: {row.get('event_type', 'Impact')}"
            ))
        return fig
    except Exception as e:
        logger.error(f"Error adding risk zones: {e}")
        return fig

if __name__ == "__main__":
    # Smoke Test
    st.set_page_config(layout="wide")

    # Mock Data
    mock_suppliers = pl.DataFrame({
        "supplier_name": ["Shenzhen Electronics", "Hamburg Logistics", "Suez Transit"],
        "lat": [22.54, 53.55, 29.97],
        "lon": [114.05, 9.99, 32.52],
        "risk_score": [85, 20, 95]
    })

    mock_layout = {
        "template": "plotly_dark",
        "margin": {"t": 0, "b": 0, "l": 0, "r": 0}
    }

    st.title("Map Component Smoke Test")
    map_fig = build_scatter_geo(mock_suppliers, mock_layout)
    st.plotly_chart(map_fig, use_container_width=True)