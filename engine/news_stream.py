import requests
import polars as pl
import streamlit as st
import logging
import xml.etree.ElementTree as ET
from typing import List, Dict, Any, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
    """Fetches real-time supply chain news from multiple RSS feeds.

    Replaces GDELT API with RSS — free, no API key, works on Streamlit Cloud.

    Args:
        query: Keyword to filter headlines (case-insensitive).

    Returns:
        pl.DataFrame: Columns — title, url, source, timestamp
    """
    results = []
    query_lower = query.lower()

    for source_name, feed_url in RSS_FEEDS.items():
        try:
            resp = requests.get(feed_url, timeout=8, headers={
                "User-Agent": "Mozilla/5.0 (SupplyChainRiskEngine/1.0)"
            })
            resp.raise_for_status()

            root = ET.fromstring(resp.content)
            # Handle both RSS and Atom formats
            items = root.findall(".//item") or root.findall(".//entry")

            for item in items[:20]:  # Max 20 per feed
                title = (
                    getattr(item.find("title"), "text", "") or ""
                ).strip()
                link = (
                    getattr(item.find("link"), "text", "") or
                    (item.find("link").get("href", "") if item.find("link") is not None else "")
                ).strip()
                pub_date = (
                    getattr(item.find("pubDate"), "text", "") or
                    getattr(item.find("updated"), "text", "") or
                    getattr(item.find("published"), "text", "") or ""
                ).strip()

                # Filter by keyword
                if query_lower in title.lower():
                    results.append({
                        "title":     title,
                        "url":       link,
                        "source":    source_name,
                        "timestamp": pub_date,
                    })

        except Exception as e:
            logger.warning(f"RSS fetch failed for {source_name}: {e}")
            continue

    if not results:
        # Return all headlines if no keyword match found
        return _fetch_all_headlines()

    return pl.DataFrame(results)


@st.cache_data(ttl=300)
def _fetch_all_headlines() -> pl.DataFrame:
    """Fallback — returns all headlines from RSS feeds without keyword filter."""
    results = []
    for source_name, feed_url in RSS_FEEDS.items():
        try:
            resp = requests.get(feed_url, timeout=8, headers={
                "User-Agent": "Mozilla/5.0 (SupplyChainRiskEngine/1.0)"
            })
            resp.raise_for_status()
            root  = ET.fromstring(resp.content)
            items = root.findall(".//item") or root.findall(".//entry")
            for item in items[:10]:
                title    = getattr(item.find("title"), "text", "").strip()
                link     = getattr(item.find("link"),  "text", "").strip()
                pub_date = getattr(item.find("pubDate"), "text", "").strip()
                if title:
                    results.append({
                        "title":     title,
                        "url":       link,
                        "source":    source_name,
                        "timestamp": pub_date,
                    })
        except Exception as e:
            logger.warning(f"Fallback RSS failed for {source_name}: {e}")
    return pl.DataFrame(results) if results else pl.DataFrame()


# ── Open-Meteo weather (FREE — no API key needed) ────────────────────────────

@st.cache_data(ttl=600)
def fetch_weather_open_meteo(lat: float, lon: float) -> Dict[str, Any]:
    """Fetches current weather for a coordinate via Open-Meteo (no API key).

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
    """Interprets Open-Meteo response into shipping risk indicators."""
    try:
        current = weather_data.get("current_weather", {})
        hourly  = weather_data.get("hourly", {})

        windspeed   = current.get("windspeed",   0)
        weathercode = current.get("weathercode", 0)
        temperature = current.get("temperature", None)

        precip_list = hourly.get("precipitation_probability", [0])
        precip_prob = max(precip_list[:6]) if precip_list else 0

        code_map = {
            0: "Clear sky",
            1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
            45: "Fog", 48: "Icy fog",
            51: "Light drizzle", 53: "Drizzle", 55: "Heavy drizzle",
            61: "Slight rain",   63: "Rain",     65: "Heavy rain",
            71: "Slight snow",   73: "Snow",      75: "Heavy snow",
            77: "Snow grains",
            80: "Slight showers", 81: "Showers", 82: "Violent showers",
            85: "Snow showers",   86: "Heavy snow showers",
            95: "Thunderstorm",
            96: "Thunderstorm w/ hail", 99: "Thunderstorm w/ heavy hail",
        }
        condition = code_map.get(weathercode, f"Code {weathercode}")

        if weathercode >= 95 or windspeed > 60:
            risk_level = "🔴 SEVERE"
        elif weathercode >= 65 or windspeed > 40 or precip_prob > 80:
            risk_level = "🟠 HIGH"
        elif weathercode >= 51 or windspeed > 25 or precip_prob > 50:
            risk_level = "🟡 MODERATE"
        else:
            risk_level = "🟢 LOW"

        return {
            "condition":   condition,
            "temperature": temperature,
            "windspeed":   windspeed,
            "precip_prob": precip_prob,
            "risk_level":  risk_level,
            "weathercode": weathercode,
        }
    except Exception as e:
        logger.error(f"Weather parse error: {e}")
        return {}


def filter_by_region(df: pl.DataFrame, region_code: str) -> pl.DataFrame:
    """Filters news DataFrame by source name (partial match)."""
    if df.is_empty():
        return df
    try:
        return df.lazy().filter(
            pl.col("source").str.contains(region_code, literal=False)
        ).collect()
    except Exception as e:
        logger.error(f"Filtering error: {e}")
        return pl.DataFrame()


if __name__ == "__main__":
    print("Smoke test — RSS Feed:")
    news_df = get_disruption_events("supply chain")
    print(f"Retrieved {len(news_df)} events.")
    print(news_df.head(3))

    print("\nSmoke test — Open-Meteo (Karachi):")
    raw    = fetch_weather_open_meteo(24.86, 67.01)
    parsed = parse_weather_risk(raw)
    print(parsed)