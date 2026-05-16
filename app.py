"""
app.py — Supply Chain Risk Engine
Entry point for the Streamlit application.
All imports are guarded with try/except to prevent crash on Streamlit Cloud.
"""

import logging
import os
import sys
import hashlib

import streamlit as st
import polars as pl

# ── Logging ──────────────────────────────────────────────────────────────────
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ── Path fix: make sure sibling packages are importable ──────────────────────
ROOT = os.path.dirname(os.path.abspath(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

# ── Internal imports (all guarded) ───────────────────────────────────────────

# theme.py
try:
    from theme import apply_theme, get_plotly_layout
    _THEME_OK = True
except Exception as e:
    logger.warning(f"theme.py import failed: {e}")
    _THEME_OK = False

# components/views.py
try:
    from components.views import (
        show_risk_overview,
        show_map_view,
        show_news_feed,
        show_scenario_page,
    )
    _VIEWS_OK = True
except Exception as e:
    logger.warning(f"components/views.py import failed: {e}")
    _VIEWS_OK = False

# engine/ingest.py
try:
    from engine.ingest import load_csv, fetch_gdelt, detect_schema
    _INGEST_OK = True
except Exception as e:
    logger.warning(f"engine/ingest.py import failed: {e}")
    _INGEST_OK = False

# engine/news_stream.py
try:
    from engine.news_stream import (
        get_disruption_events,
        filter_by_region,
        fetch_weather_open_meteo,
        parse_weather_risk,
    )
    _NEWS_OK = True
    _WEATHER_OK = True
except Exception as e:
    logger.warning(f"engine/news_stream.py import failed: {e}")
    _NEWS_OK = False
    _WEATHER_OK = False

# engine/risk_model.py
try:
    from engine.risk_model import compute_risk_score
    _RISK_MODEL_OK = True
except Exception as e:
    logger.warning(f"engine/risk_model.py import failed: {e}")
    _RISK_MODEL_OK = False

# engine/scenario_sim.py
try:
    from engine.scenario_sim import (
        simulate_disruption,
        calc_inventory_impact,
        project_lead_time_change,
    )
    _SIM_OK = True
except Exception as e:
    logger.warning(f"engine/scenario_sim.py import failed: {e}")
    _SIM_OK = False

# database/risk_queries.py
try:
    import duckdb
    from database.risk_queries import (
        init_db,
        query_by_region,
        query_top_risk_suppliers,
        query_monthly_trend,
    )
    _DB_OK = True
except Exception as e:
    logger.warning(f"database/risk_queries.py import failed: {e}")
    _DB_OK = False

# components/alerts.py
try:
    from components.alerts import (
        detect_anomalies,
        get_critical_suppliers,
        render_alert_banner,
    )
    _ALERTS_OK = True
except Exception as e:
    logger.warning(f"components/alerts.py import failed: {e}")
    _ALERTS_OK = False

# components/map_viz.py
try:
    from components.map_viz import build_scatter_geo, build_choropleth, add_risk_zones
    _MAP_OK = True
except Exception as e:
    logger.warning(f"components/map_viz.py import failed: {e}")
    _MAP_OK = False

# utils/pdf_gen.py
try:
    from utils.pdf_gen import generate_report
    _PDF_OK = True
except Exception as e:
    logger.warning(f"utils/pdf_gen.py import failed: {e}")
    _PDF_OK = False


# ── Login System ──────────────────────────────────────────────────────────────
VALID_CREDENTIALS = {
    "Ali-datasmith": hashlib.sha256("SC@Risk#2025!".encode()).hexdigest(),
}

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def render_login_page() -> bool:
    """Enterprise-grade $5000-tier login page with full-bleed map, premium card, animations."""

    st.markdown("""
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">

    <style>
    /* ── GLOBAL RESET ── */
    html, body, [data-testid="stAppViewContainer"],
    [data-testid="stMain"], .main, .block-container {
        margin: 0 !important; padding: 0 !important;
        background: #030d07 !important;
        font-family: 'Inter', -apple-system, sans-serif !important;
    }
    [data-testid="stSidebar"]          { display: none !important; }
    [data-testid="stHeader"]           { display: none !important; }
    [data-testid="stToolbar"]          { display: none !important; }
    [data-testid="stDecoration"]       { display: none !important; }
    footer                             { display: none !important; }
    .block-container { max-width: 100% !important; padding: 0 !important; }

    /* ── FULLSCREEN BACKGROUND ── */
    .ent-bg {
        position: relative;
        min-height: 100vh;
        width: 100%;
        background: #030d07;
        display: flex;
        align-items: center;
        justify-content: center;
        overflow: hidden;
        padding: 40px 20px;
    }

    /* Animated dot grid */
    .ent-bg::before {
        content: '';
        position: absolute;
        inset: 0;
        background-image:
            radial-gradient(circle, rgba(0,200,80,0.07) 1px, transparent 1px);
        background-size: 36px 36px;
        animation: gridDrift 20s linear infinite;
    }
    @keyframes gridDrift {
        0%   { background-position: 0 0; }
        100% { background-position: 36px 36px; }
    }

    /* Corner accent brackets */
    .ent-bg::after {
        content: '';
        position: absolute;
        top: 28px; left: 28px;
        width: 80px; height: 80px;
        border-top: 1px solid rgba(0,200,80,0.18);
        border-left: 1px solid rgba(0,200,80,0.18);
    }

    /* Top scanning bar */
    .scan-bar {
        position: absolute;
        top: 0; left: 0; right: 0; height: 2px;
        background: linear-gradient(90deg,
            transparent 0%, rgba(0,200,80,0.0) 20%,
            #00e64d 50%, rgba(0,229,100,0.0) 80%, transparent 100%);
        animation: scanPulse 4s ease-in-out infinite;
    }
    @keyframes scanPulse {
        0%, 100% { opacity: 0.3; transform: scaleX(0.6); }
        50%       { opacity: 1;   transform: scaleX(1); }
    }

    /* Bottom-right bracket */
    .br-bracket {
        position: absolute;
        bottom: 28px; right: 28px;
        width: 80px; height: 80px;
        border-bottom: 1px solid rgba(0,200,80,0.18);
        border-right:  1px solid rgba(0,200,80,0.18);
    }

    /* ── STATUS BAR (top of page) ── */
    .ent-status-bar {
        position: absolute;
        top: 16px; left: 50%; transform: translateX(-50%);
        display: flex; align-items: center; gap: 20px;
        background: rgba(0,0,0,0.5);
        border: 1px solid rgba(0,200,80,0.12);
        border-radius: 40px;
        padding: 6px 18px;
        z-index: 10;
        white-space: nowrap;
    }
    .status-item {
        display: flex; align-items: center; gap: 5px;
        font-size: 10px; font-weight: 500;
        color: rgba(0,200,80,0.45);
        letter-spacing: 1.5px; text-transform: uppercase;
        font-family: 'JetBrains Mono', monospace;
    }
    .status-dot {
        width: 5px; height: 5px; border-radius: 50%;
        background: #00e64d;
        animation: blink 2s ease-in-out infinite;
    }
    .status-dot.amber  { background: #f59e0b; animation-delay: 0.7s; }
    .status-dot.cyan   { background: #00e5ff; animation-delay: 1.4s; }
    @keyframes blink {
        0%,100% { opacity: 1; } 50% { opacity: 0.25; }
    }

    /* ── MAIN CARD ── */
    .ent-card {
        position: relative; z-index: 5;
        width: 460px;
        background: rgba(4, 14, 8, 0.97);
        border: 1px solid rgba(0,200,80,0.22);
        border-radius: 20px;
        overflow: hidden;
        animation: cardAppear 0.6s cubic-bezier(0.16,1,0.3,1) both;
    }
    @keyframes cardAppear {
        from { opacity: 0; transform: translateY(24px) scale(0.97); }
        to   { opacity: 1; transform: translateY(0)   scale(1); }
    }

    /* Card top accent line */
    .ent-card::before {
        content: '';
        position: absolute;
        top: 0; left: 10%; right: 10%; height: 1px;
        background: linear-gradient(90deg,
            transparent, rgba(0,230,77,0.6), rgba(0,229,255,0.4), rgba(0,230,77,0.6), transparent);
    }

    /* ── MAP SECTION ── */
    .map-section {
        width: 100%; height: 210px;
        background: #020a05;
        position: relative;
        overflow: hidden;
        border-bottom: 1px solid rgba(0,200,80,0.14);
    }
    .map-section svg { display: block; width: 100%; height: 100%; }

    /* Horizontal scan line over map */
    .map-scan {
        position: absolute;
        left: 0; right: 0; height: 1px;
        background: linear-gradient(90deg,
            transparent, rgba(0,230,77,0.5), rgba(0,229,255,0.3), rgba(0,230,77,0.5), transparent);
        animation: mapScanAnim 5s linear infinite;
        pointer-events: none;
    }
    @keyframes mapScanAnim {
        0%   { top: 0;     opacity: 0; }
        5%   {             opacity: 1; }
        95%  {             opacity: 1; }
        100% { top: 210px; opacity: 0; }
    }

    /* Brand overlay at map bottom */
    .map-brand-overlay {
        position: absolute;
        bottom: 0; left: 0; right: 0;
        padding: 36px 22px 16px;
        background: linear-gradient(to top,
            rgba(4,14,8,1) 0%, rgba(4,14,8,0.92) 55%, transparent 100%);
        display: flex; align-items: flex-end; justify-content: space-between;
    }
    .brand-left  { display: flex; align-items: center; gap: 13px; }
    .brand-shield {
        width: 44px; height: 44px;
        background: rgba(0,200,80,0.07);
        border: 1px solid rgba(0,200,80,0.32);
        border-radius: 12px;
        display: flex; align-items: center; justify-content: center;
        flex-shrink: 0;
    }
    .brand-shield svg { width: 24px; height: 24px; }
    .brand-title {
        font-size: 18px; font-weight: 700;
        color: #00e64d;
        letter-spacing: 4px; text-transform: uppercase;
        line-height: 1;
        font-family: 'Inter', sans-serif;
    }
    .brand-sub {
        font-size: 9.5px; font-weight: 400;
        color: rgba(0,180,70,0.45);
        letter-spacing: 2.5px; text-transform: uppercase;
        margin-top: 5px;
        font-family: 'JetBrains Mono', monospace;
    }
    .live-pill {
        display: flex; align-items: center; gap: 6px;
        background: rgba(0,200,80,0.06);
        border: 1px solid rgba(0,200,80,0.2);
        border-radius: 20px; padding: 5px 10px;
    }
    .live-dot {
        width: 6px; height: 6px; border-radius: 50%;
        background: #00e64d;
        animation: blink 1.6s ease-in-out infinite;
    }
    .live-label {
        font-size: 9px; font-weight: 600;
        color: rgba(0,200,80,0.6);
        letter-spacing: 2px; text-transform: uppercase;
        font-family: 'JetBrains Mono', monospace;
    }

    /* ── FORM SECTION ── */
    .ent-form { padding: 26px 28px 22px; }

    /* Welcome row */
    .welcome-row {
        display: flex; align-items: center; gap: 10px;
        margin-bottom: 22px;
    }
    .welcome-line { flex: 1; height: 1px; background: rgba(0,150,60,0.14); }
    .welcome-text {
        font-size: 9.5px; font-weight: 500;
        color: rgba(0,170,65,0.4);
        letter-spacing: 3px; text-transform: uppercase;
        font-family: 'JetBrains Mono', monospace;
        white-space: nowrap;
    }

    /* Field labels */
    .ent-label {
        display: flex; align-items: center; gap: 6px;
        font-size: 10px; font-weight: 600;
        color: rgba(0,180,70,0.5);
        letter-spacing: 2.5px; text-transform: uppercase;
        margin-bottom: 7px;
        font-family: 'JetBrains Mono', monospace;
    }
    .ent-label-icon { font-size: 12px; opacity: 0.7; }

    /* Override Streamlit text inputs */
    div[data-testid="stTextInput"] input {
        background: rgba(0,0,0,0.45) !important;
        border: 1px solid rgba(0,150,60,0.22) !important;
        border-radius: 10px !important;
        color: #00e64d !important;
        font-size: 13px !important;
        font-family: 'JetBrains Mono', monospace !important;
        letter-spacing: 0.5px !important;
        padding: 11px 14px !important;
        transition: border-color 0.2s !important;
    }
    div[data-testid="stTextInput"] input:focus {
        border-color: rgba(0,200,80,0.55) !important;
        box-shadow: 0 0 0 3px rgba(0,200,80,0.06) !important;
    }
    div[data-testid="stTextInput"] input::placeholder {
        color: rgba(0,150,60,0.25) !important;
    }
    div[data-testid="stTextInput"] label {
        display: none !important;
    }

    /* Login button */
    div[data-testid="stButton"] > button {
        width: 100% !important;
        background: rgba(0,200,80,0.07) !important;
        border: 1px solid rgba(0,200,80,0.38) !important;
        border-radius: 11px !important;
        color: #00e64d !important;
        font-size: 11.5px !important;
        font-weight: 700 !important;
        letter-spacing: 3.5px !important;
        text-transform: uppercase !important;
        padding: 14px 20px !important;
        font-family: 'Inter', sans-serif !important;
        transition: all 0.22s ease !important;
        cursor: pointer !important;
        margin-top: 6px !important;
    }
    div[data-testid="stButton"] > button:hover {
        background: rgba(0,200,80,0.14) !important;
        border-color: rgba(0,220,80,0.6) !important;
        transform: translateY(-1px) !important;
    }
    div[data-testid="stButton"] > button:active {
        transform: translateY(0px) !important;
    }

    /* Error/success alerts — restyle */
    div[data-testid="stAlert"] {
        background: rgba(220,38,38,0.08) !important;
        border: 1px solid rgba(220,38,38,0.25) !important;
        border-radius: 10px !important;
        font-size: 12px !important;
        margin-top: 10px !important;
    }

    /* Divider */
    .ent-divider {
        height: 1px;
        background: rgba(0,150,60,0.12);
        margin: 18px 0 16px;
    }

    /* Credentials box */
    .creds-box {
        background: rgba(0,200,80,0.04);
        border: 1px solid rgba(0,200,80,0.13);
        border-radius: 11px;
        padding: 14px 16px;
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 12px;
    }
    .cred-item {}
    .cred-key {
        font-size: 9px; font-weight: 600;
        color: rgba(0,170,65,0.4);
        letter-spacing: 2px; text-transform: uppercase;
        font-family: 'JetBrains Mono', monospace;
        margin-bottom: 4px;
    }
    .cred-val {
        font-size: 12.5px; font-weight: 500;
        color: rgba(0,220,80,0.75);
        font-family: 'JetBrains Mono', monospace;
        letter-spacing: 0.3px;
    }
    .creds-icon {
        font-size: 10px; margin-right: 4px; opacity: 0.6;
    }

    /* Powered by footer */
    .ent-footer {
        padding: 14px 28px 18px;
        border-top: 1px solid rgba(0,150,60,0.1);
        display: flex; align-items: center; justify-content: space-between;
    }
    .footer-left {
        font-size: 9px; font-weight: 400;
        color: rgba(0,150,60,0.3);
        letter-spacing: 1.5px; text-transform: uppercase;
        font-family: 'JetBrains Mono', monospace;
    }
    .footer-left span {
        color: rgba(0,200,80,0.55);
        font-weight: 600;
    }
    .footer-version {
        font-size: 9px;
        color: rgba(0,150,60,0.25);
        font-family: 'JetBrains Mono', monospace;
        letter-spacing: 1px;
    }

    /* Streamlit block spacing fix */
    div[data-testid="stVerticalBlock"] > div { gap: 0 !important; }
    .stTextInput { margin-bottom: 12px !important; }
    </style>
    """, unsafe_allow_html=True)

    # ── Full world map SVG ─────────────────────────────────────────────────────
    MAP_SVG = """
    <div class="map-section">
      <div class="map-scan"></div>
      <svg viewBox="0 0 460 210" xmlns="http://www.w3.org/2000/svg"
           style="display:block;width:100%;height:100%;">
        <defs>
          <radialGradient id="bgG" cx="50%" cy="45%" r="65%">
            <stop offset="0%"   stop-color="#031408"/>
            <stop offset="100%" stop-color="#010704"/>
          </radialGradient>
          <filter id="cg" x="-30%" y="-30%" width="160%" height="160%">
            <feGaussianBlur in="SourceGraphic" stdDeviation="1.8" result="b"/>
            <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
          </filter>
          <filter id="dg" x="-80%" y="-80%" width="360%" height="360%">
            <feGaussianBlur stdDeviation="5" result="b"/>
            <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
          </filter>
        </defs>

        <rect width="460" height="210" fill="url(#bgG)"/>

        <!-- Lat/lon grid -->
        <g stroke="#092814" stroke-width="0.5">
          <line x1="0" y1="35"  x2="460" y2="35"/>
          <line x1="0" y1="70"  x2="460" y2="70"/>
          <line x1="0" y1="105" x2="460" y2="105"/>
          <line x1="0" y1="140" x2="460" y2="140"/>
          <line x1="0" y1="175" x2="460" y2="175"/>
          <line x1="46"  y1="0" x2="46"  y2="210"/>
          <line x1="92"  y1="0" x2="92"  y2="210"/>
          <line x1="138" y1="0" x2="138" y2="210"/>
          <line x1="184" y1="0" x2="184" y2="210"/>
          <line x1="230" y1="0" x2="230" y2="210"/>
          <line x1="276" y1="0" x2="276" y2="210"/>
          <line x1="322" y1="0" x2="322" y2="210"/>
          <line x1="368" y1="0" x2="368" y2="210"/>
          <line x1="414" y1="0" x2="414" y2="210"/>
        </g>

        <!-- Equator -->
        <line x1="0" y1="105" x2="460" y2="105"
              stroke="#00e64d" stroke-width="0.5" stroke-dasharray="8,6" opacity="0.18"/>

        <!-- CONTINENTS — bright visible fills -->
        <!-- North America -->
        <path d="M42,18 L75,16 L95,24 L102,36 L100,50 L90,62 L80,72 L73,82
                 L62,86 L52,78 L44,66 L36,52 L34,36 Z"
              fill="#0c5c2c" stroke="#00d44a" stroke-width="1.4" filter="url(#cg)"/>
        <path d="M73,82 L79,86 L74,94 L67,91 Z"
              fill="#0c5c2c" stroke="#00d44a" stroke-width="0.8"/>
        <!-- South America -->
        <path d="M76,98 L94,94 L108,102 L114,122 L110,146 L100,160
                 L84,163 L70,154 L66,136 L68,116 Z"
              fill="#0c5c2c" stroke="#00d44a" stroke-width="1.4" filter="url(#cg)"/>
        <!-- Greenland -->
        <path d="M90,5 L106,3 L112,12 L106,20 L92,21 Z"
              fill="#083d1c" stroke="#00aa38" stroke-width="0.9"/>
        <!-- Europe -->
        <path d="M190,20 L210,18 L222,25 L224,36 L216,44 L204,48
                 L192,45 L184,37 L182,28 Z"
              fill="#0c5c2c" stroke="#00d44a" stroke-width="1.4" filter="url(#cg)"/>
        <path d="M200,10 L210,7 L214,17 L202,19 Z"
              fill="#0c5c2c" stroke="#00d44a" stroke-width="0.8"/>
        <!-- Africa -->
        <path d="M186,52 L208,50 L222,58 L228,74 L226,100 L220,120
                 L208,130 L194,132 L180,124 L174,106 L174,82 L178,62 Z"
              fill="#0c5c2c" stroke="#00d44a" stroke-width="1.4" filter="url(#cg)"/>
        <!-- Middle East -->
        <path d="M228,52 L244,50 L252,58 L250,72 L238,79 L226,74 Z"
              fill="#0c5c2c" stroke="#00d44a" stroke-width="1.1"/>
        <!-- Russia -->
        <path d="M208,12 L290,10 L314,18 L318,30 L302,40 L274,43
                 L248,40 L228,36 L214,26 Z"
              fill="#0c5c2c" stroke="#00d44a" stroke-width="1.4" filter="url(#cg)"/>
        <!-- India -->
        <path d="M260,54 L276,52 L282,62 L278,80 L268,90 L256,80 L252,64 Z"
              fill="#0c5c2c" stroke="#00d44a" stroke-width="1.1"/>
        <!-- China/East Asia -->
        <path d="M284,26 L330,23 L344,32 L346,50 L332,60 L308,64
                 L288,58 L278,44 Z"
              fill="#0c5c2c" stroke="#00d44a" stroke-width="1.4" filter="url(#cg)"/>
        <!-- SE Asia islands -->
        <path d="M316,84 L332,82 L338,90 L328,98 L314,96 Z"
              fill="#0c5c2c" stroke="#00d44a" stroke-width="0.9"/>
        <path d="M338,90 L354,88 L360,96 L350,104 L336,102 Z"
              fill="#0c5c2c" stroke="#00d44a" stroke-width="0.9"/>
        <!-- Japan -->
        <path d="M350,30 L358,27 L363,36 L356,44 L348,40 Z"
              fill="#0c5c2c" stroke="#00d44a" stroke-width="0.9"/>
        <!-- Australia -->
        <path d="M324,120 L360,116 L378,126 L380,150 L366,164
                 L340,167 L318,158 L308,142 L310,128 Z"
              fill="#0c5c2c" stroke="#00d44a" stroke-width="1.4" filter="url(#cg)"/>
        <!-- NZ -->
        <path d="M384,152 L390,148 L394,158 L388,163 Z"
              fill="#0c5c2c" stroke="#00d44a" stroke-width="0.8"/>

        <!-- Shipping routes -->
        <g stroke="#00cc44" stroke-width="0.8" stroke-dasharray="5,4" fill="none" opacity="0.38">
          <path d="M52,66 Q198,42 340,42"/>
          <path d="M196,36 Q148,24 90,50"/>
          <path d="M340,42 Q328,68 322,92"/>
          <path d="M240,65 Q218,52 196,36"/>
          <path d="M322,92 Q348,108 354,138"/>
          <path d="M266,74 Q254,68 240,65"/>
          <path d="M108,102 Q92,118 84,135"/>
        </g>

        <!-- Risk hotspots -->
        <!-- Shanghai -->
        <circle cx="340" cy="42" r="4.5" fill="#00FF41" opacity="0.92">
          <animate attributeName="r"       values="4.5;8.5;4.5" dur="2.2s" repeatCount="indefinite"/>
          <animate attributeName="opacity" values="0.92;0.22;0.92" dur="2.2s" repeatCount="indefinite"/>
        </circle>
        <!-- Rotterdam -->
        <circle cx="196" cy="36" r="3.8" fill="#00e5ff" opacity="0.88">
          <animate attributeName="r"       values="3.8;7.5;3.8" dur="2.8s" repeatCount="indefinite"/>
          <animate attributeName="opacity" values="0.88;0.22;0.88" dur="2.8s" repeatCount="indefinite"/>
        </circle>
        <!-- Los Angeles -->
        <circle cx="52" cy="66" r="3.8" fill="#00FF41" opacity="0.85">
          <animate attributeName="r"       values="3.8;7;3.8" dur="3.1s" repeatCount="indefinite"/>
          <animate attributeName="opacity" values="0.85;0.2;0.85" dur="3.1s" repeatCount="indefinite"/>
        </circle>
        <!-- Singapore -->
        <circle cx="322" cy="92" r="3.5" fill="#00e5ff" opacity="0.85">
          <animate attributeName="r"       values="3.5;7;3.5" dur="2.5s" repeatCount="indefinite"/>
          <animate attributeName="opacity" values="0.85;0.2;0.85" dur="2.5s" repeatCount="indefinite"/>
        </circle>
        <!-- Dubai -->
        <circle cx="240" cy="65" r="3.5" fill="#a3ff00" opacity="0.82">
          <animate attributeName="r"       values="3.5;6.5;3.5" dur="3.4s" repeatCount="indefinite"/>
          <animate attributeName="opacity" values="0.82;0.2;0.82" dur="3.4s" repeatCount="indefinite"/>
        </circle>
        <!-- Mumbai -->
        <circle cx="266" cy="74" r="3.2" fill="#00e5ff" opacity="0.8">
          <animate attributeName="r"       values="3.2;6;3.2" dur="2.9s" repeatCount="indefinite"/>
          <animate attributeName="opacity" values="0.8;0.18;0.8" dur="2.9s" repeatCount="indefinite"/>
        </circle>
        <!-- New York -->
        <circle cx="90" cy="50" r="3.2" fill="#00FF41" opacity="0.8">
          <animate attributeName="r"       values="3.2;6;3.2" dur="3.6s" repeatCount="indefinite"/>
          <animate attributeName="opacity" values="0.8;0.18;0.8" dur="3.6s" repeatCount="indefinite"/>
        </circle>
        <!-- Karachi -->
        <circle cx="254" cy="62" r="2.8" fill="#a3ff00" opacity="0.75">
          <animate attributeName="r"       values="2.8;5.5;2.8" dur="2.6s" repeatCount="indefinite"/>
          <animate attributeName="opacity" values="0.75;0.18;0.75" dur="2.6s" repeatCount="indefinite"/>
        </circle>

        <!-- Map labels -->
        <text x="8" y="205" fill="#00e64d" font-size="7.5" font-family="'JetBrains Mono',monospace"
              opacity="0.35" letter-spacing="1.2">GLOBAL SUPPLY CHAIN RISK MAP</text>
        <circle cx="368" cy="202" r="3" fill="#00e5ff" opacity="0.5">
          <animate attributeName="opacity" values="0.5;0.1;0.5" dur="1.5s" repeatCount="indefinite"/>
        </circle>
        <text x="374" y="206" fill="#00e5ff" font-size="7.5" font-family="'JetBrains Mono',monospace"
              opacity="0.35" letter-spacing="1.5">LIVE</text>
      </svg>

      <!-- Brand overlay -->
      <div class="map-brand-overlay">
        <div class="brand-left">
          <div class="brand-shield">
            <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M12 2L4 5.5V11C4 15.55 7.41 19.74 12 21C16.59 19.74 20 15.55 20 11V5.5L12 2Z"
                    fill="rgba(0,200,80,0.12)" stroke="#00e64d" stroke-width="1.4"
                    stroke-linejoin="round"/>
              <path d="M9 12L11 14L15 10" stroke="#00e64d" stroke-width="1.5"
                    stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </div>
          <div>
            <div class="brand-title">RISK ENGINE</div>
            <div class="brand-sub">Supply Chain Intelligence Platform</div>
          </div>
        </div>
        <div class="live-pill">
          <div class="live-dot"></div>
          <span class="live-label">LIVE</span>
        </div>
      </div>
    </div>
    """

    # ── Page wrapper open ──────────────────────────────────────────────────────
    st.markdown("""
    <div class="ent-bg">
      <div class="scan-bar"></div>
      <div class="br-bracket"></div>
      <div class="ent-status-bar">
        <div class="status-item"><div class="status-dot"></div>Systems Nominal</div>
        <div class="status-item"><div class="status-dot amber"></div>24 Active Alerts</div>
        <div class="status-item"><div class="status-dot cyan"></div>847 Suppliers</div>
      </div>
      <div class="ent-card">
    """, unsafe_allow_html=True)

    # Map section
    st.markdown(MAP_SVG, unsafe_allow_html=True)

    # Form section open
    st.markdown("""
    <div class="ent-form">
      <div class="welcome-row">
        <div class="welcome-line"></div>
        <div class="welcome-text">Welcome to Supply Chain Risk Engine</div>
        <div class="welcome-line"></div>
      </div>
      <div class="ent-label"><span class="ent-label-icon">◈</span> Username</div>
    </div>
    """, unsafe_allow_html=True)

    username = st.text_input(
        "Username", placeholder="Enter your username", key="login_username", label_visibility="collapsed"
    )

    st.markdown('<div style="padding: 0 28px;"><div class="ent-label"><span class="ent-label-icon">◈</span> Password</div></div>', unsafe_allow_html=True)

    password = st.text_input(
        "Password", type="password", placeholder="Enter your password",
        key="login_password", label_visibility="collapsed"
    )

    login_btn = st.button("⬡  AUTHENTICATE  ⬡", use_container_width=True, type="primary")

    if login_btn:
        if not username or not password:
            st.error("⚠️  Both fields are required to authenticate.")
        elif username in VALID_CREDENTIALS and hash_password(password) == VALID_CREDENTIALS[username]:
            st.session_state["authenticated"] = True
            st.session_state["logged_in_user"] = username
            st.rerun()
        else:
            st.error("⛔  Access denied. Invalid credentials.")

    # Credentials + footer
    st.markdown("""
      <div class="ent-divider"></div>
      <div class="creds-box">
        <div class="cred-item">
          <div class="cred-key"><span class="creds-icon">◈</span>Username</div>
          <div class="cred-val">Ali-datasmith</div>
        </div>
        <div class="cred-item">
          <div class="cred-key"><span class="creds-icon">◈</span>Password</div>
          <div class="cred-val">SC@Risk#2025!</div>
        </div>
      </div>
    </div>
    <!-- end ent-form -->

    <div class="ent-footer">
      <div class="footer-left">Powered by &nbsp;<span>Ali-datasmith</span></div>
      <div class="footer-version">v2.4.1 &nbsp;·&nbsp; Enterprise</div>
    </div>

    </div>
    <!-- end ent-card -->
    </div>
    <!-- end ent-bg -->
    """, unsafe_allow_html=True)

    return False


# ── Session State ─────────────────────────────────────────────────────────────
def _init_session_state() -> None:
    defaults = {
        "df": pl.DataFrame(),
        "page": "Dashboard",
        "news_df": pl.DataFrame(),
        "sim_df": pl.DataFrame(),
        "authenticated": False,
        "logged_in_user": "",
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val


# ── Sidebar ───────────────────────────────────────────────────────────────────
def render_sidebar() -> None:
    st.sidebar.title("🛡 RISK ENGINE")
    st.sidebar.markdown(f"👤 `{st.session_state.get('logged_in_user', '')}`")
    st.sidebar.markdown("---")

    uploaded_file = st.sidebar.file_uploader("📂 Upload Suppliers CSV", type=["csv"])
    if uploaded_file:
        try:
            content = uploaded_file.read()
            from io import BytesIO
            df = pl.read_csv(BytesIO(content))
            df = df.rename({col: col.lower() for col in df.columns})
            alias_map = {
                "vendor": "supplier", "name": "supplier", "supplier_name": "supplier",
                "supplier_region": "region", "country": "region", "area": "region",
                "latitude": "lat", "y": "lat",
                "longitude": "lon", "lng": "lon", "x": "lon",
                "risk": "risk_score", "score": "risk_score", "rating": "risk_score",
            }
            rename_needed = {
                old: new for old, new in alias_map.items()
                if old in df.columns and new not in df.columns
            }
            if rename_needed:
                df = df.rename(rename_needed)
            st.session_state["df"] = df
            st.sidebar.success(f"✅ Loaded {df.height} suppliers")
        except Exception as e:
            logger.error(f"CSV ingestion error: {e}")
            st.sidebar.error("❌ Failed to parse CSV. Check format.")

    st.sidebar.markdown("---")

    st.session_state["page"] = st.sidebar.radio(
        "📌 Navigation",
        ["Dashboard", "Map View", "Intelligence Feed", "Scenario Lab", "PDF Report", "Weather Monitor"],
        index=["Dashboard", "Map View", "Intelligence Feed",
               "Scenario Lab", "PDF Report", "Weather Monitor"].index(
            st.session_state.get("page", "Dashboard")
        ),
    )

    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🔌 Module Status")
    status_flags = {
        "Theme": _THEME_OK, "Views": _VIEWS_OK, "Ingest": _INGEST_OK,
        "Risk Model": _RISK_MODEL_OK, "Scenario Sim": _SIM_OK,
        "Database": _DB_OK, "Alerts": _ALERTS_OK, "Map": _MAP_OK,
        "PDF": _PDF_OK, "News": _NEWS_OK, "Weather": _WEATHER_OK,
    }
    for module, ok in status_flags.items():
        st.sidebar.markdown(f"{'🟢' if ok else '🔴'} `{module}`")

    st.sidebar.markdown("---")
    if st.sidebar.button("🚪 Logout", use_container_width=True):
        st.session_state["authenticated"] = False
        st.session_state["logged_in_user"] = ""
        st.rerun()


# ── Page: Dashboard ───────────────────────────────────────────────────────────
def page_dashboard(data: pl.DataFrame) -> None:
    st.title("📊 Executive Risk Dashboard")

    if _ALERTS_OK:
        try:
            anomalies = detect_anomalies(data)
            col = "supplier_name" if "supplier_name" in data.columns else "supplier"
            temp = data.rename({col: "supplier_name"}) if col != "supplier_name" else data
            criticals = get_critical_suppliers(temp)
            render_alert_banner(len(criticals), len(anomalies))
        except Exception as e:
            logger.error(f"Alert banner error: {e}")
    else:
        st.info("ℹ️ Alerts module not loaded.")

    if _VIEWS_OK:
        try:
            show_risk_overview(data)
        except Exception as e:
            logger.error(f"Risk overview error: {e}")
            _fallback_overview(data)
    else:
        _fallback_overview(data)

    if _DB_OK and not data.is_empty():
        st.subheader("🗄 Top Risk Suppliers (DuckDB Query)")
        try:
            con = duckdb.connect(":memory:")
            con.register("risk_data_view", data.to_pandas())
            score_col = "risk_score" if "risk_score" in data.columns else data.columns[0]
            sup_col   = "supplier"   if "supplier"   in data.columns else data.columns[0]
            top_df = con.execute(
                f"SELECT {sup_col} AS supplier_name, {score_col} AS risk_score "
                f"FROM risk_data_view ORDER BY {score_col} DESC LIMIT 10"
            ).pl()
            st.dataframe(top_df, use_container_width=True)
        except Exception as e:
            logger.error(f"DuckDB query error: {e}")
            st.dataframe(data.head(10).to_pandas(), use_container_width=True)


def _fallback_overview(data: pl.DataFrame) -> None:
    try:
        import plotly.express as px
        col1, col2, col3 = st.columns(3)
        avg  = data["risk_score"].mean() if "risk_score" in data.columns else 0
        high = data.filter(pl.col("risk_score") > 75).height if "risk_score" in data.columns else 0
        col1.metric("Avg Risk Score", f"{avg:.1f}")
        col2.metric("High Risk Suppliers", high)
        col3.metric("Total Suppliers", data.height)
        if "risk_score" in data.columns:
            fig = px.histogram(data.to_pandas(), x="risk_score", nbins=20,
                               title="Risk Score Distribution",
                               color_discrete_sequence=["#00FF41"])
            fig.update_layout(paper_bgcolor="rgba(0,0,0,0)",
                              plot_bgcolor="rgba(0,0,0,0)", font_color="#00FF41")
            st.plotly_chart(fig, use_container_width=True)
    except Exception as e:
        logger.error(f"Fallback overview error: {e}")
        st.dataframe(data.to_pandas(), use_container_width=True)


# ── Page: Map View ────────────────────────────────────────────────────────────
def page_map(data: pl.DataFrame) -> None:
    st.title("🌍 Global Risk Map")
    has_geo = "lat" in data.columns and "lon" in data.columns
    if not has_geo:
        st.warning("⚠️ Columns 'lat' and 'lon' not found in dataset. Map unavailable.")
        st.info("Please ensure your CSV has latitude and longitude columns.")
        return

    layout_cfg = {}
    if _THEME_OK:
        try:
            layout_cfg = get_plotly_layout()
        except Exception:
            pass

    if _MAP_OK:
        try:
            sup_col  = "supplier" if "supplier" in data.columns else data.columns[0]
            map_data = data
            if "supplier_name" not in data.columns:
                map_data = data.with_columns(pl.col(sup_col).alias("supplier_name"))
            fig = build_scatter_geo(map_data, layout_cfg)
            st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            logger.error(f"map_viz error: {e}")
            _fallback_map(data, layout_cfg)
    elif _VIEWS_OK:
        try:
            show_map_view(data)
        except Exception as e:
            _fallback_map(data, layout_cfg)
    else:
        _fallback_map(data, layout_cfg)


def _fallback_map(data: pl.DataFrame, layout_cfg: dict) -> None:
    import plotly.express as px
    try:
        sup_col = "supplier" if "supplier" in data.columns else data.columns[0]
        fig = px.scatter_geo(
            data.to_pandas(), lat="lat", lon="lon", hover_name=sup_col,
            size="risk_score" if "risk_score" in data.columns else None,
            color="risk_score" if "risk_score" in data.columns else None,
            color_continuous_scale="RdYlGn_r", projection="natural earth",
            title="Supplier Geographic Risk Exposure",
        )
        if layout_cfg:
            fig.update_layout(**layout_cfg)
        st.plotly_chart(fig, use_container_width=True)
    except Exception as e:
        logger.error(f"Fallback map error: {e}")
        st.error("Map could not be rendered. Check lat/lon columns.")


# ── Page: Intelligence Feed ───────────────────────────────────────────────────
def page_news() -> None:
    st.title("📡 Supply Chain Intelligence Feed")
    st.caption("Live news via RSS — BBC Business · Financial Times · Supply Chain Dive · Reuters")
    st.markdown("---")

    col_a, col_b = st.columns([4, 1])
    with col_a:
        keyword = st.text_input("🔍 Search Keyword", value="supply chain",
                                placeholder="e.g. logistics, tariff, port strike")
    with col_b:
        st.markdown("<br>", unsafe_allow_html=True)
        fetch_clicked = st.button("🔄 Fetch", use_container_width=True)

    if fetch_clicked:
        if not _NEWS_OK:
            st.error("News module not loaded. Check engine/news_stream.py")
            return
        with st.spinner("Fetching live headlines..."):
            try:
                news_df = get_disruption_events(keyword)
                st.session_state["news_df"] = news_df
            except Exception as e:
                logger.error(f"RSS fetch error: {e}")
                st.warning("Could not fetch news. Check internet connection.")
                return

    news_df = st.session_state.get("news_df", pl.DataFrame())

    if news_df.is_empty():
        st.info("👆 Enter a keyword and click Fetch to load live headlines.")
        return

    sources = news_df["source"].unique().to_list() if "source" in news_df.columns else []
    m1, m2  = st.columns(2)
    m1.metric("📰 Articles Found", news_df.height)
    m2.metric("📡 Sources Active", len(sources))
    st.markdown("---")

    if sources:
        selected_sources = st.multiselect("Filter by Source", sources, default=sources)
        if selected_sources:
            news_df = news_df.filter(pl.col("source").is_in(selected_sources))

    st.subheader(f"📋 {news_df.height} Headlines")
    for row in news_df.iter_rows(named=True):
        title     = row.get("title", "No Title")
        url       = row.get("url", "#")
        source    = row.get("source", "Unknown")
        timestamp = row.get("timestamp", "")
        with st.expander(f"**{source}** — {title[:90]}{'...' if len(title) > 90 else ''}"):
            st.markdown(f"**{title}**")
            st.caption(f"🕐 {timestamp}  |  📡 {source}")
            if url and url != "#":
                st.markdown(f"[🔗 Read Full Article]({url})")


# ── Page: Scenario Lab ────────────────────────────────────────────────────────
def page_scenario(data: pl.DataFrame) -> None:
    st.title("⚗️ Risk Scenario Simulator")
    st.info("Simulate the impact of global disruptions on your supply chain.")

    with st.container():
        st.subheader("🌐 Region Disruption Simulator")
        col1, col2 = st.columns(2)
        with col1:
            regions_available = (
                data["region"].unique().to_list()
                if "region" in data.columns else ["APAC", "EMEA", "NAMER", "LATAM"]
            )
            affected  = st.multiselect("Affected Regions", regions_available,
                                       default=regions_available[:1])
            intensity = st.slider("Disruption Intensity (multiplier)", 1.0, 5.0, 2.0, 0.1)
        with col2:
            st.markdown("**What this simulates:**")
            st.markdown("- Risk score amplification in selected regions")
            st.markdown("- Inventory shortfall exposure")
            st.markdown("- Lead time projection under stress")

        if st.button("▶ Run Disruption Simulation"):
            if data.is_empty():
                st.warning("Upload a CSV first.")
            elif "risk_score" not in data.columns:
                st.error("'risk_score' column required for simulation.")
            else:
                try:
                    if _SIM_OK:
                        sim_df = simulate_disruption(data, intensity, affected)
                    else:
                        sim_df = data.with_columns(
                            pl.when(pl.col("region").is_in(affected))
                            .then((pl.col("risk_score") * intensity).clip(0, 100))
                            .otherwise(pl.col("risk_score"))
                            .alias("simulated_risk_score")
                        ) if "region" in data.columns else data.with_columns(
                            (pl.col("risk_score") * intensity).clip(0, 100)
                            .alias("simulated_risk_score")
                        )
                    st.session_state["sim_df"] = sim_df
                    st.success("✅ Simulation complete!")
                    st.dataframe(sim_df.to_pandas(), use_container_width=True)

                    if "simulated_risk_score" in sim_df.columns:
                        import plotly.graph_objects as go
                        sup_col = "supplier" if "supplier" in sim_df.columns else sim_df.columns[0]
                        fig = go.Figure()
                        fig.add_bar(x=sim_df[sup_col].to_list(),
                                    y=sim_df["risk_score"].to_list(),
                                    name="Baseline Risk", marker_color="#00AAFF")
                        fig.add_bar(x=sim_df[sup_col].to_list(),
                                    y=sim_df["simulated_risk_score"].to_list(),
                                    name="Simulated Risk", marker_color="#FF4444")
                        fig.update_layout(barmode="group", title="Baseline vs Simulated Risk",
                                          paper_bgcolor="rgba(0,0,0,0)",
                                          plot_bgcolor="rgba(0,0,0,0)", font_color="#00FF41")
                        st.plotly_chart(fig, use_container_width=True)
                except Exception as e:
                    logger.error(f"Simulation error: {e}")
                    st.error(f"Simulation failed: {e}")

    st.markdown("---")
    st.subheader("📦 Inventory Impact Calculator")
    c1, c2, c3 = st.columns(3)
    with c1:
        inventory = st.number_input("Current Inventory (units)", min_value=0.0, value=1000.0)
    with c2:
        demand    = st.number_input("Daily Demand (units/day)",  min_value=0.1, value=100.0)
    with c3:
        lead_time = st.number_input("Lead Time (days)",          min_value=1,   value=15)

    if st.button("📊 Calculate Inventory Risk"):
        try:
            if _SIM_OK:
                result = calc_inventory_impact(inventory, demand, lead_time)
            else:
                days_cover     = inventory / demand if demand > 0 else 999
                shortfall_prob = min((lead_time / (days_cover + 1e-9)) * 0.5, 1.0)
                result = {"days_cover": days_cover, "shortfall_probability": shortfall_prob}
            col_a, col_b = st.columns(2)
            col_a.metric("Days of Cover",         f"{result['days_cover']:.1f} days")
            col_b.metric("Shortfall Probability", f"{result['shortfall_probability']*100:.1f}%")
            if result["shortfall_probability"] > 0.5:
                st.error("🚨 High shortfall risk — consider safety stock increase.")
            elif result["shortfall_probability"] > 0.25:
                st.warning("⚠️ Moderate shortfall risk.")
            else:
                st.success("✅ Inventory coverage is adequate.")
        except Exception as e:
            st.error(f"Calculation failed: {e}")

    st.markdown("---")
    st.subheader("🚢 Lead Time Projector")
    c4, c5, c6 = st.columns(3)
    with c4:
        base_lt      = st.number_input("Base Lead Time (days)", min_value=1.0, value=10.0)
    with c5:
        congestion   = st.slider("Port Congestion Index", 1.0, 2.0, 1.3, 0.05)
    with c6:
        labor_strike = st.checkbox("Active Labor Strike?")

    if st.button("📈 Project Lead Time"):
        try:
            if _SIM_OK:
                projected = project_lead_time_change(base_lt, congestion, labor_strike)
            else:
                projected = round(base_lt * congestion * (1.4 if labor_strike else 1.0), 2)
            st.metric("Projected Lead Time", f"{projected} days",
                      delta=f"+{projected - base_lt:.1f} days", delta_color="inverse")
        except Exception as e:
            st.error(f"Projection failed: {e}")


# ── Page: PDF Report ──────────────────────────────────────────────────────────
def page_pdf(data: pl.DataFrame) -> None:
    st.title("📄 Automated PDF Risk Report")
    summary_text = st.text_area(
        "Executive Summary",
        value="This report presents a comprehensive analysis of global supply chain risks "
              "based on real-time data ingested by the Risk Engine.",
        height=120,
    )
    if st.button("🖨 Generate PDF Report"):
        if data.is_empty():
            st.warning("No data to report. Please upload a CSV first.")
            return
        if not _PDF_OK:
            st.error("PDF module (utils/pdf_gen.py) is not available.")
            return
        with st.spinner("Generating report..."):
            try:
                report_df = data
                if "risk_score" not in report_df.columns:
                    st.error("'risk_score' column required for PDF generation.")
                    return
                if "supplier" in report_df.columns and "supplier_name" not in report_df.columns:
                    report_df = report_df.with_columns(
                        pl.col("supplier").alias("supplier_name")
                    )
                pdf_bytes = generate_report(report_df, summary_text)
                if pdf_bytes:
                    st.success("✅ Report generated successfully!")
                    st.download_button(
                        label="⬇️ Download PDF Report",
                        data=pdf_bytes,
                        file_name="supply_chain_risk_report.pdf",
                        mime="application/pdf",
                    )
                else:
                    st.error("PDF generation returned empty output.")
            except Exception as e:
                logger.error(f"PDF generation error: {e}")
                st.error(f"PDF generation failed: {e}")


# ── Page: Weather Monitor ─────────────────────────────────────────────────────
def page_weather(data: pl.DataFrame) -> None:
    st.title("🌦️ Shipping Route Weather Monitor")
    st.caption("Powered by Open-Meteo · Free · No API key required")
    st.markdown("---")

    has_geo = "lat" in data.columns and "lon" in data.columns

    if has_geo and not data.is_empty():
        sup_col       = "supplier" if "supplier" in data.columns else data.columns[0]
        supplier_list = data[sup_col].to_list()
        st.subheader("📍 Check Weather at Supplier Location")
        selected_supplier = st.selectbox("Select Supplier", supplier_list)
        row        = data.filter(pl.col(sup_col) == selected_supplier).row(0, named=True)
        lat        = float(row["lat"])
        lon        = float(row["lon"])
        region_col = next((c for c in ["region", "supplier_region"] if c in data.columns), None)
        region_val = row.get(region_col, "—") if region_col else "—"
        c1, c2, c3 = st.columns(3)
        c1.metric("Supplier", selected_supplier)
        c2.metric("Region",   str(region_val))
        c3.metric("Coords",   f"{lat:.3f}, {lon:.3f}")
    else:
        st.info("No lat/lon in dataset — enter coordinates manually.")
        col1, col2 = st.columns(2)
        with col1:
            lat = st.number_input("Latitude",  value=24.86, format="%.4f")
        with col2:
            lon = st.number_input("Longitude", value=67.01, format="%.4f")

    st.markdown("---")

    if st.button("🔄 Fetch Weather Conditions"):
        if not _WEATHER_OK:
            st.error("Weather module not loaded. Check engine/news_stream.py")
            return
        with st.spinner("Fetching from Open-Meteo..."):
            try:
                raw     = fetch_weather_open_meteo(lat, lon)
                weather = parse_weather_risk(raw)
                if not weather:
                    st.error("Could not parse weather data.")
                    return

                st.subheader("📊 Current Conditions")
                m1, m2, m3, m4 = st.columns(4)
                m1.metric("🌡️ Temperature", f"{weather['temperature']} °C" if weather['temperature'] is not None else "N/A")
                m2.metric("💨 Wind Speed",  f"{weather['windspeed']} km/h")
                m3.metric("🌧️ Precip. Prob.", f"{weather['precip_prob']} %")
                m4.metric("☁️ Condition",   weather["condition"])

                st.markdown("### 🚢 Shipping Risk Assessment")
                risk = weather["risk_level"]
                if "SEVERE"   in risk: st.error(f"{risk} — Severe weather. Shipping disruption highly likely.")
                elif "HIGH"   in risk: st.warning(f"{risk} — Adverse conditions. Expect significant delays.")
                elif "MODERATE" in risk: st.info(f"{risk} — Some weather impact possible. Monitor closely.")
                else:                  st.success(f"{risk} — Conditions are favourable for shipping.")

                hourly    = raw.get("hourly", {})
                wind_vals = hourly.get("windspeed_10m", [])
                time_vals = hourly.get("time", [])

                if wind_vals and time_vals:
                    import plotly.graph_objects as go
                    fig = go.Figure()
                    fig.add_trace(go.Scatter(
                        x=time_vals[:24], y=wind_vals[:24],
                        mode="lines+markers",
                        line=dict(color="#00FF41", width=2),
                        fill="tozeroy", fillcolor="rgba(0,255,65,0.1)",
                        name="Wind Speed (km/h)",
                    ))
                    fig.update_layout(
                        title="24-Hour Wind Speed Forecast",
                        xaxis_title="Time", yaxis_title="Wind Speed (km/h)",
                        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                        font_color="#00FF41",
                        xaxis=dict(gridcolor="#1A1A1A", linecolor="#00FF41"),
                        yaxis=dict(gridcolor="#1A1A1A", linecolor="#00FF41"),
                        margin=dict(t=40, b=40, l=40, r=40),
                    )
                    st.plotly_chart(fig, use_container_width=True)

                precip_vals = hourly.get("precipitation_probability", [])
                if precip_vals and time_vals:
                    import plotly.graph_objects as go
                    fig2 = go.Figure()
                    fig2.add_trace(go.Bar(
                        x=time_vals[:24], y=precip_vals[:24],
                        marker_color=["#FF4444" if v > 80 else "#FFA500" if v > 50 else "#00FF41"
                                      for v in precip_vals[:24]],
                        name="Precipitation Probability (%)",
                    ))
                    fig2.update_layout(
                        title="24-Hour Precipitation Probability",
                        xaxis_title="Time", yaxis_title="Probability (%)",
                        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                        font_color="#00FF41",
                        xaxis=dict(gridcolor="#1A1A1A", linecolor="#00FF41"),
                        yaxis=dict(gridcolor="#1A1A1A", linecolor="#00FF41"),
                        margin=dict(t=40, b=40, l=40, r=40),
                    )
                    st.plotly_chart(fig2, use_container_width=True)

            except Exception as e:
                logger.error(f"Weather page error: {e}")
                st.error(f"Weather fetch failed: {e}")


# ── Router ────────────────────────────────────────────────────────────────────
def route_page(data: pl.DataFrame) -> None:
    page = st.session_state.get("page", "Dashboard")
    try:
        if page == "Dashboard":        page_dashboard(data)
        elif page == "Map View":       page_map(data)
        elif page == "Intelligence Feed": page_news()
        elif page == "Scenario Lab":   page_scenario(data)
        elif page == "PDF Report":     page_pdf(data)
        elif page == "Weather Monitor": page_weather(data)
    except Exception as e:
        logger.error(f"Routing error on '{page}': {e}")
        st.error(f"Page '{page}' crashed: {e}")
        st.info("Try uploading a fresh CSV or reloading the app.")


# ── Main ──────────────────────────────────────────────────────────────────────
def main() -> None:
    st.set_page_config(
        page_title="SupplyChain Risk Engine",
        page_icon="🛡", layout="wide",
        initial_sidebar_state="expanded",
    )
    _init_session_state()

    # ── Authentication Gate ───────────────────────────────────────────────────
    if not st.session_state.get("authenticated", False):
        render_login_page()
        st.stop()

    # ── Authenticated: normal app flow ────────────────────────────────────────
    if _THEME_OK:
        try:
            apply_theme()
        except Exception as e:
            logger.warning(f"Theme application failed: {e}")
    render_sidebar()

    data = st.session_state.get("df", pl.DataFrame())
    page = st.session_state.get("page", "Dashboard")

    if data.is_empty() and page not in ("Intelligence Feed",):
        st.title("🛡 Supply Chain Risk Engine")
        st.markdown("---")
        st.warning("👈 **Upload a Suppliers CSV in the sidebar to begin.**")
        st.info(
            "**Expected columns:** `supplier`, `region`, `risk_score`  \n"
            "**Optional (for map):** `lat`, `lon`  \n"
            "**Optional:** `industry`, `lead_time_days`, `financial_risk`, etc."
        )
        with st.expander("📋 Sample CSV format"):
            sample = pl.DataFrame({
                "supplier":   ["Acme Logistics", "Shenzhen Mfg", "Berlin Parts"],
                "region":     ["NAMER", "APAC", "EMEA"],
                "lat":        [34.05, 22.54, 52.52],
                "lon":        [-118.24, 114.05, 13.40],
                "risk_score": [82.5, 45.2, 12.8],
                "industry":   ["Logistics", "Electronics", "Automotive"],
            })
            st.dataframe(sample.to_pandas(), use_container_width=True)
        st.stop()

    route_page(data)


if __name__ == "__main__":
    main()