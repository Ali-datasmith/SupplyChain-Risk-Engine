import requests
import polars as pl
import streamlit as st
import logging
<<<<<<< HEAD
import xml.etree.ElementTree as ET
=======
>>>>>>> origin/main
from typing import List, Dict, Any, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

<<<<<<< HEAD
# ── RSS Feed Sources (Free, No API Key, Streamlit Cloud Compatible) ──────────
RSS_FEEDS = {
    "Reuters Supply Chain": "https://feeds.reuters.com/reuters/businessNews",
    "BBC Business":         "https://feeds.bbci.co.uk/news/business/rss.xml",
    "Financial Times":      "https://www.ft.com/rss/home/uk",
    "Supply Chain Dive":    "https://www.supplychaindive.com/feeds/news/",
    "Logistics MgmtNews":   "https://www.logisticsmgmt.com/rss/news",
}

@st.cache_data(ttl=300)
def get_disruption_events(query: str = "supply chain disruption") -> pl.DataFrame:
    results = []
    query_lower = query.lower()
    for source_name, feed_url in RSS_FEEDS.items():
        try:
            resp = requests.get(feed_url, timeout=8, headers={
                "User-Agent": "Mozilla/5.0 (SupplyChainRiskEngine/1.0)"
            })
            resp.raise_for_status()
            root  = ET.fromstring(resp.content)
            items = root.findall(".//item") or root.findall(".//entry")
            for item in items[:20]:
                title    = (getattr(item.find("title"),   "text", "") or "").strip()
                link     = (getattr(item.find("link"),    "text", "") or "").strip()
                pub_date = (
                    getattr(item.find("pubDate"),   "text", "") or
                    getattr(item.find("updated"),   "text", "") or
                    getattr(item.find("published"), "text", "") or ""
                ).strip()
                if query_lower in title.lower():
                    results.append({"title": title, "url": link,
                                    "source": source_name, "timestamp": pub_date})
        except Exception as e:
            logger.warning(f"RSS fetch failed for {source_name}: {e}")
    if not results:
        return _fetch_all_headlines()
    return pl.DataFrame(results)


@st.cache_data(ttl=300)
def _fetch_all_headlines() -> pl.DataFrame:
    results = []
    for source_name, feed_url in RSS_FEEDS.items():
        try:
            resp  = requests.get(feed_url, timeout=8, headers={"User-Agent": "Mozilla/5.0"})
            resp.raise_for_status()
            root  = ET.fromstring(resp.content)
            items = root.findall(".//item") or root.findall(".//entry")
            for item in items[:10]:
                title    = getattr(item.find("title"),   "text", "").strip()
                link     = getattr(item.find("link"),    "text", "").strip()
                pub_date = getattr(item.find("pubDate"), "text", "").strip()
                if title:
                    results.append({"title": title, "url": link,
                                    "source": source_name, "timestamp": pub_date})
        except Exception as e:
            logger.warning(f"Fallback RSS failed for {source_name}: {e}")
    return pl.DataFrame(results) if results else pl.DataFrame()


@st.cache_data(ttl=600)
def fetch_weather_open_meteo(lat: float, lon: float) -> dict:
    try:
        url    = "https://api.open-meteo.com/v1/forecast"
        params = {
            "latitude": lat, "longitude": lon,
            "current_weather": True,
            "hourly": "temperature_2m,precipitation_probability,windspeed_10m,weathercode,visibility",
            "forecast_days": 1,
        }
        r = requests.get(url, params=params, timeout=8)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        logger.error(f"Open-Meteo error: {e}")
        return {}


def parse_weather_risk(weather_data: dict) -> dict:
    try:
        current     = weather_data.get("current_weather", {})
        hourly      = weather_data.get("hourly", {})
        windspeed   = current.get("windspeed",   0)
        weathercode = current.get("weathercode", 0)
        temperature = current.get("temperature", None)
        precip_list = hourly.get("precipitation_probability", [0])
        precip_prob = max(precip_list[:6]) if precip_list else 0
        code_map = {
            0:"Clear sky",1:"Mainly clear",2:"Partly cloudy",3:"Overcast",
            45:"Fog",48:"Icy fog",51:"Light drizzle",53:"Drizzle",55:"Heavy drizzle",
            61:"Slight rain",63:"Rain",65:"Heavy rain",71:"Slight snow",73:"Snow",
            75:"Heavy snow",80:"Slight showers",81:"Showers",82:"Violent showers",
            95:"Thunderstorm",96:"Thunderstorm w/ hail",99:"Thunderstorm w/ heavy hail",
        }
        condition = code_map.get(weathercode, f"Code {weathercode}")
        if weathercode >= 95 or windspeed > 60:   risk_level = "🔴 SEVERE"
        elif weathercode >= 65 or windspeed > 40:  risk_level = "🟠 HIGH"
        elif weathercode >= 51 or windspeed > 25:  risk_level = "🟡 MODERATE"
        else:                                       risk_level = "🟢 LOW"
        return {"condition": condition, "temperature": temperature,
                "windspeed": windspeed, "precip_prob": precip_prob,
                "risk_level": risk_level, "weathercode": weathercode}
=======

@st.cache_data(ttl=300)
def get_disruption_events(query: str = "supply chain disruption") -> pl.DataFrame:
    """Fetches real-time global disruption events via the GDELT Project API.

    Args:
        query: Keywords to filter global news events.

    Returns:
        pl.DataFrame: A Polars DataFrame containing event titles, sources, and links.
    """
    try:
        url = "https://api.gdeltproject.org/api/v2/doc/doc"
        params = {
            "query":      query,
            "mode":       "artlist",
            "format":     "json",
            "maxrecords": 75,
        }
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json().get("articles", [])
        if not data:
            return pl.DataFrame()

        df = pl.DataFrame(data)
        return df.select([
            pl.col("title"),
            pl.col("url"),
            pl.col("sourcecountry").alias("country_code"),
            pl.col("seendate").alias("timestamp"),
        ])
    except Exception as e:
        logger.error(f"GDELT API error: {e}")
        st.warning("Could not retrieve global news stream.")
        return pl.DataFrame()


# ── Open-Meteo weather (FREE — no API key needed) ────────────────────────────

@st.cache_data(ttl=600)
def fetch_weather_open_meteo(lat: float, lon: float) -> Dict[str, Any]:
    """Fetches current weather conditions for a coordinate using Open-Meteo API.

    Open-Meteo is completely free with no API key required.
    Docs: https://open-meteo.com/en/docs

    Args:
        lat: Latitude of the location.
        lon: Longitude of the location.

    Returns:
        Dict with current weather data or empty dict on failure.
    """
    try:
        url = "https://api.open-meteo.com/v1/forecast"
        params = {
            "latitude":        lat,
            "longitude":       lon,
            "current_weather": True,
            "hourly": ",".join([
                "temperature_2m",
                "precipitation_probability",
                "windspeed_10m",
                "weathercode",
                "visibility",
            ]),
            "forecast_days": 1,
        }
        response = requests.get(url, params=params, timeout=8)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logger.error(f"Open-Meteo API error: {e}")
        return {}


def parse_weather_risk(weather_data: Dict[str, Any]) -> Dict[str, Any]:
    """Interprets Open-Meteo response into shipping risk indicators.

    Args:
        weather_data: Raw response dict from fetch_weather_open_meteo().

    Returns:
        Dict with parsed weather metrics and a risk label.
    """
    try:
        current = weather_data.get("current_weather", {})
        hourly  = weather_data.get("hourly", {})

        windspeed   = current.get("windspeed",    0)
        weathercode = current.get("weathercode",  0)
        temperature = current.get("temperature",  None)

        # Precipitation probability — take max of next 6 hours
        precip_list = hourly.get("precipitation_probability", [0])
        precip_prob = max(precip_list[:6]) if precip_list else 0

        # WMO weather code → human label
        # https://open-meteo.com/en/docs#weathervariables
        code_map = {
            0:  "Clear sky",
            1:  "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
            45: "Fog", 48: "Icy fog",
            51: "Light drizzle", 53: "Drizzle", 55: "Heavy drizzle",
            61: "Slight rain",   63: "Rain",   65: "Heavy rain",
            71: "Slight snow",   73: "Snow",   75: "Heavy snow",
            77: "Snow grains",
            80: "Slight showers", 81: "Showers", 82: "Violent showers",
            85: "Snow showers",   86: "Heavy snow showers",
            95: "Thunderstorm",
            96: "Thunderstorm w/ hail", 99: "Thunderstorm w/ heavy hail",
        }
        condition = code_map.get(weathercode, f"Code {weathercode}")

        # Shipping risk heuristic
        if weathercode >= 95 or windspeed > 60:
            risk_level = "🔴 SEVERE"
        elif weathercode >= 65 or windspeed > 40 or precip_prob > 80:
            risk_level = "🟠 HIGH"
        elif weathercode >= 51 or windspeed > 25 or precip_prob > 50:
            risk_level = "🟡 MODERATE"
        else:
            risk_level = "🟢 LOW"

        return {
            "condition":    condition,
            "temperature":  temperature,
            "windspeed":    windspeed,
            "precip_prob":  precip_prob,
            "risk_level":   risk_level,
            "weathercode":  weathercode,
        }
>>>>>>> origin/main
    except Exception as e:
        logger.error(f"Weather parse error: {e}")
        return {}


<<<<<<< HEAD
def filter_by_region(df, region_code: str):
    if df.is_empty():
        return df
    try:
        return df.lazy().filter(
            pl.col("source").str.contains(region_code, literal=False)
        ).collect()
    except Exception as e:
        logger.error(f"Filtering error: {e}")
        return pl.DataFrame()
=======
def filter_by_region(df: pl.DataFrame, region_code: str) -> pl.DataFrame:
    """Filters the news stream DataFrame by a specific country/region code."""
    if df.is_empty():
        return df
    try:
        return df.lazy().filter(pl.col("country_code") == region_code).collect()
    except Exception as e:
        logger.error(f"Filtering error: {e}")
        return pl.DataFrame()


if __name__ == "__main__":
    print("Smoke test — Open-Meteo (Karachi):")
    raw = fetch_weather_open_meteo(24.86, 67.01)
    parsed = parse_weather_risk(raw)
    print(parsed)

    print("\nSmoke test — GDELT:")
    news_df = get_disruption_events("port strike")
    print(f"Retrieved {len(news_df)} events.")
>>>>>>> origin/main
