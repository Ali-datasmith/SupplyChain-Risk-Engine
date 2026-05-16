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
    # ── Core Supply Chain & Logistics ──────────────────────────────────────
    "Supply Chain Dive":     "https://www.supplychaindive.com/feeds/news/",
    "Logistics Management":  "https://www.logisticsmgmt.com/rss/news",
    "FreightWaves":          "https://www.freightwaves.com/news/feed",
    "DC Velocity":           "https://dcvelocity.com/feed/",
    # ── Trade, Shipping & Port News ────────────────────────────────────────
    "JOC (Port/Shipping)":   "https://www.joc.com/rss.xml",
    "Hellenic Shipping News": "https://www.hellenicshippingnews.com/feed/",
    # ── Global Trade & Risk ────────────────────────────────────────────────
    "Reuters Trade":         "https://feeds.reuters.com/reuters/companyNews",
    "Bloomberg Supply Chain": "https://feeds.bloomberg.com/markets/news.rss",
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
    except Exception as e:
        logger.error(f"Weather parse error: {e}")
        return {}


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