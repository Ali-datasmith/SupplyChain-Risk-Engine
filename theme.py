import streamlit as st
import plotly.graph_objects as go
import logging
from typing import Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def apply_theme() -> None:
    """Applies a Neon/Terminal CSS aesthetic to the Streamlit application.

    Injects custom CSS to handle dark backgrounds, neon green accents, and
    terminal-style font families across all Streamlit components.
    """
    terminal_css = """
    <style>
        /* Main background and base text */
        .stApp {
            background-color: #0E1117;
            color: #00FF41;
            font-family: 'Courier New', Courier, monospace;
        }

        /* Sidebar styling */
        [data-testid="stSidebar"] {
            background-color: #050505;
            border-right: 1px solid #00FF41;
        }

        /* Neon Borders for cards/metrics */
        div[data-testid="stMetricValue"] {
            color: #00FF41 !important;
            text-shadow: 0 0 10px #00FF41;
        }

        /* Input fields and terminal buttons */
        .stTextInput>div>div>input, .stSelectbox>div>div>div {
            background-color: #000000 !important;
            color: #00FF41 !important;
            border: 1px solid #00FF41 !important;
        }

        /* Titles and Headers */
        h1, h2, h3 {
            color: #00FF41 !important;
            text-transform: uppercase;
            letter-spacing: 2px;
            text-shadow: 0 0 5px #00FF41;
        }

        /* Custom Scrollbar */
        ::-webkit-scrollbar { width: 8px; }
        ::-webkit-scrollbar-track { background: #050505; }
        ::-webkit-scrollbar-thumb { background: #00FF41; border-radius: 4px; }
    </style>
    """
    try:
        st.markdown(terminal_css, unsafe_allow_html=True)
    except Exception as e:
        logger.error(f"Failed to apply terminal theme: {e}")
        st.warning("Visual engine encountered an error. Reverting to default.")

def get_plotly_layout() -> Dict[str, Any]:
    """Provides a standardized dark terminal layout for Plotly visualizations.

    Returns:
        Dict[str, Any]: Configuration dictionary for fig.update_layout().
    """
    try:
        return {
            "template": "plotly_dark",
            "paper_bgcolor": "rgba(0,0,0,0)",
            "plot_bgcolor": "rgba(0,0,0,0)",
            "font": {"color": "#00FF41", "family": "Courier New"},
            "xaxis": {
                "gridcolor": "#1A1A1A",
                "linecolor": "#00FF41",
                "zerolinecolor": "#00FF41",
            },
            "yaxis": {
                "gridcolor": "#1A1A1A",
                "linecolor": "#00FF41",
                "zerolinecolor": "#00FF41",
            },
            "margin": {"t": 40, "b": 40, "l": 40, "r": 40},
            "hovermode": "closest",
        }
    except Exception as e:
        logger.error(f"Error generating Plotly layout: {e}")
        return {}

def _run_smoke_test() -> None:
    """Internal test to verify theme rendering."""
    st.set_page_config(page_title="Theme Test", layout="wide")
    apply_theme()
    st.title("📟 Risk Engine Terminal")
    st.sidebar.markdown("### SYSTEM STATUS: ONLINE")

    col1, col2 = st.columns(2)
    with col1:
        st.metric("Critical Risks", 12, delta="+2")
    with col2:
        fig = go.Figure(go.Scatter(x=[1, 2, 3], y=[10, 15, 13], line=dict(color="#00FF41")))
        fig.update_layout(**get_plotly_layout())
        st.plotly_chart(fig, use_container_width=True)

if __name__ == "__main__":
    _run_smoke_test()