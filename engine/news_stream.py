import requests
import polars as pl
import streamlit as st
import logging
import os
from typing import List, Dict, Any, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@st.cache_data(ttl=300)
def get_disruption_events(query: str = "supply chain disruption") -> pl.DataFrame:
    """Fetches real-time global disruption events via the GDELT Project API.

    Args:
        query: Keywords to filter global news events.

    Returns:
        pl.DataFrame: A Polars DataFrame containing event titles, sources, and links.
    """
    try:
        # GDELT Full Text Search API v2
        url = "https://api.gdeltproject.org/api/v2/doc/doc"
        params = {
            "query": query,
            "mode": "artlist",
            "format": "json",
            "maxrecords": 75
        }
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json().get("articles", [])

        if not data:
            return pl.DataFrame()

        df = pl.DataFrame(data)
        # Standardize columns
        return df.select([
            pl.col("title"),
            pl.col("url"),
            pl.col("sourcecountry").alias("country_code"),
            pl.col("seendate").alias("timestamp")
        ])
    except Exception as e:
        logger.error(f"GDELT API error: {e}")
        st.warning("Could not retrieve global news stream.")
        return pl.DataFrame()

@st.cache_data(ttl=600)
def parse_weather_alerts(lat: float, lon: float) -> List[Dict[str, Any]]:
    """Fetches and parses active weather alerts for specific coordinates.

    Args:
        lat: Latitude of the location.
        lon: Longitude of the location.

    Returns:
        List[Dict[str, Any]]: A list of active alerts with description and severity.
    """
    api_key = st.secrets.get("OPENWEATHER_API_KEY") or os.environ.get("OPENWEATHER_API_KEY")
    if not api_key:
        logger.warning("Weather API Key missing.")
        return []

    try:
        # OpenWeather One Call API (requires valid subscription/key)
        url = f"https://api.openweathermap.org/data/3.0/onecall?lat={lat}&lon={lon}&exclude=minutely,hourly,daily&appid={api_key}"
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        return response.json().get("alerts", [])
    except Exception as e:
        logger.error(f"Weather Alert API error: {e}")
        return []

def filter_by_region(df: pl.DataFrame, region_code: str) -> pl.DataFrame:
    """Filters the news stream DataFrame by a specific country/region code.

    Args:
        df: The Polars DataFrame containing news events.
        region_code: ISO country code to filter by.

    Returns:
        pl.DataFrame: Filtered Polars DataFrame.
    """
    if df.is_empty():
        return df

    try:
        # Rule 6: Use lazy execution for potential scalability
        return df.lazy().filter(pl.col("country_code") == region_code).collect()
    except Exception as e:
        logger.error(f"Filtering error: {e}")
        return pl.DataFrame()

if __name__ == "__main__":
    # Smoke Test
    print("Executing News Stream Smoke Test...")
    news_df = get_disruption_events("port strike")
    if not news_df.is_empty():
        print(f"Retrieved {len(news_df)} events.")
        filtered = filter_by_region(news_df, "US")
        print(f"Filtered to US: {len(filtered)} events.")
    else:
        print("No news data retrieved (Check network/GDELT status).")