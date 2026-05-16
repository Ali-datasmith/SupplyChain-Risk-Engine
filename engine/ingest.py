import streamlit as st
import polars as pl
import requests
import logging
from io import BytesIO
from typing import Optional, Dict, Any, List

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@st.cache_data(ttl=600)
def load_csv(uploaded_file: Any) -> pl.DataFrame:
    """Loads and parses a CSV file into a Polars DataFrame.

    Args:
        uploaded_file: The Streamlit UploadedFile object.

    Returns:
        pl.DataFrame: The loaded data or an empty DataFrame on failure.
    """
    try:
        content = uploaded_file.read()
        df = pl.read_csv(BytesIO(content))

        # Rule 6: Use lazy frames for potential large datasets
        if len(df) > 10000:
            return df.lazy().collect()
        return df
    except Exception as e:
        logger.error(f"CSV Load Error: {e}")
        st.warning("Failed to parse the uploaded CSV file.")
        return pl.DataFrame()

@st.cache_data(ttl=300)
def fetch_gdelt(keyword: str, max_records: int = 50) -> pl.DataFrame:
    """Pulls latest global events from GDELT Project API.

    Args:
        keyword: Search term for supply chain disruptions.
        max_records: Maximum records to retrieve.

    Returns:
        pl.DataFrame: Event data or empty DataFrame.
    """
    try:
        url = f"https://api.gdeltproject.org/api/v2/doc/doc?query={keyword}&mode=artlist&format=json&maxrecords={max_records}"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json().get("articles", [])
        return pl.DataFrame(data) if data else pl.DataFrame()
    except Exception as e:
        logger.error(f"GDELT Fetch Error: {e}")
        st.warning("Unable to fetch global event stream.")
        return pl.DataFrame()

@st.cache_data(ttl=900)
def fetch_weather(lat: float, lon: float) -> Dict[str, Any]:
    """Retrieves real-time weather data for a logistics node.

    Args:
        lat: Latitude coordinate.
        lon: Longitude coordinate.

    Returns:
        Dict[str, Any]: Weather data or empty dict.
    """
    api_key = st.secrets.get("WEATHER_API_KEY") or os.environ.get("WEATHER_API_KEY")
    if not api_key:
        logger.warning("Weather API Key missing.")
        return {}

    try:
        url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={api_key}&units=metric"
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logger.error(f"Weather API Error: {e}")
        return {}

def detect_schema(df: pl.DataFrame) -> Dict[str, str]:
    """Analyzes DataFrame to map columns to risk engine requirements.

    Args:
        df: Input Polars DataFrame.

    Returns:
        Dict[str, str]: Mapping of detected columns to standard keys.
    """
    schema_map = {}
    cols = [c.lower() for c in df.columns]

    # Simple heuristic mapping
    mapping_logic = {
        "supplier": ["supplier", "vendor", "name"],
        "lat": ["latitude", "lat", "y"],
        "lon": ["longitude", "lon", "lng", "x"],
        "score": ["risk", "score", "rating"]
    }

    for key, aliases in mapping_logic.items():
        found = next((c for c in df.columns if c.lower() in aliases), None)
        if found:
            schema_map[key] = found

    return schema_map

if __name__ == "__main__":
    # Smoke Test
    test_df = pl.DataFrame({"Supplier": ["A"], "Lat": [24.86], "Lon": [67.0]})
    print("Schema Detection:", detect_schema(test_df))
    print("GDELT Mock Pull:", fetch_gdelt("port strike").head(2))