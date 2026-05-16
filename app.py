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
    """Renders the login page. Returns True if login is successful."""
    st.markdown(
        """
        <style>
        [data-testid="stAppViewContainer"] {
            background: linear-gradient(135deg, #0a0a0a 0%, #0d1117 50%, #0a0f1e 100%);
        }
        [data-testid="stSidebar"] { display: none; }
        .login-container {
            max-width: 420px;
            margin: 60px auto 0 auto;
            padding: 40px 36px 36px 36px;
            background: rgba(0, 255, 65, 0.04);
            border: 1px solid rgba(0, 255, 65, 0.25);
            border-radius: 16px;
            box-shadow: 0 0 40px rgba(0, 255, 65, 0.08);
        }
        .login-title {
            text-align: center;
            color: #00FF41;
            font-size: 2rem;
            font-weight: 800;
            letter-spacing: 2px;
            margin-bottom: 4px;
            text-shadow: 0 0 20px rgba(0,255,65,0.5);
        }
        .login-subtitle {
            text-align: center;
            color: rgba(0, 255, 65, 0.6);
            font-size: 0.85rem;
            letter-spacing: 3px;
            text-transform: uppercase;
            margin-bottom: 32px;
        }
        .login-divider {
            border: none;
            border-top: 1px solid rgba(0,255,65,0.15);
            margin: 24px 0;
        }
        .credentials-box {
            background: rgba(0,255,65,0.05);
            border: 1px solid rgba(0,255,65,0.2);
            border-radius: 8px;
            padding: 14px 18px;
            margin-top: 20px;
            font-size: 0.82rem;
            color: rgba(0,255,65,0.75);
        }
        .credentials-box b { color: #00FF41; }
        </style>
        """,
        unsafe_allow_html=True,
    )

    col_l, col_c, col_r = st.columns([1, 2, 1])
    with col_c:
        st.markdown('<div class="login-container">', unsafe_allow_html=True)
        st.markdown('<div class="login-title">🛡 RISK ENGINE</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="login-subtitle">Welcome to Supply Chain Risk Engine</div>',
            unsafe_allow_html=True,
        )

        username = st.text_input(
            "Username",
            placeholder="Enter your username",
            key="login_username",
        )
        password = st.text_input(
            "Password",
            type="password",
            placeholder="Enter your password",
            key="login_password",
        )

        st.markdown("")
        login_btn = st.button("🔐  LOGIN", use_container_width=True, type="primary")

        if login_btn:
            if not username or not password:
                st.error("⚠️ Please enter both username and password.")
            elif username in VALID_CREDENTIALS and hash_password(password) == VALID_CREDENTIALS[username]:
                st.session_state["authenticated"] = True
                st.session_state["logged_in_user"] = username
                st.rerun()
            else:
                st.error("❌ Invalid username or password.")

        st.markdown('<hr class="login-divider">', unsafe_allow_html=True)
        st.markdown(
            """
            <div class="credentials-box">
            🔑 <b>Login Credentials</b><br><br>
            <b>Username:</b> Ali-datasmith<br>
            <b>Password:</b> SC@Risk#2025!
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown("</div>", unsafe_allow_html=True)

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