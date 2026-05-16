# 🛡️ Global Supply Chain Risk Engine

> **A real-time, AI-powered supply chain risk monitoring dashboard built with Python, Streamlit, Polars, DuckDB, and Plotly.**

---

## 📸 App Screenshot

<!-- ============================================================
     EDIT ZONE 1 — Replace this block with your app screenshot
     Example: ![App Screenshot](assets/screenshot.png)
     ============================================================ -->

> 🖼️ **[ PASTE YOUR APP SCREENSHOT HERE ]**

---

## 🎬 Demo Video

<!-- ============================================================
     EDIT ZONE 2 — Replace this block with your demo video
     For YouTube: [![Demo Video](thumbnail.png)](https://youtube.com/your-link)
     For GIF:     ![Demo GIF](assets/demo.gif)
     ============================================================ -->

> 🎥 **[ PASTE YOUR DEMO VIDEO / GIF HERE ]**

---

## 🌐 Live App

[![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://supplychain-risk-engine-r8djbttt6eah48khhsfcze.streamlit.app/)

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Features](#-features)
- [Tech Stack](#-tech-stack)
- [Project Structure](#-project-structure)
- [Getting Started](#-getting-started)
- [CSV Format](#-csv-format)
- [Module Breakdown](#-module-breakdown)
- [Deployment](#-deployment)
- [License](#-license)

---

## 🔍 Overview

The **Global Supply Chain Risk Engine** is a professional-grade dashboard that ingests supplier data, computes multi-dimensional risk scores, visualizes global exposure on an interactive world map, and generates automated PDF audit reports — all in real time.

It is designed to help procurement teams, risk analysts, and supply chain managers identify critical vulnerabilities before they become disruptions.

---

## ✨ Features

| Feature | Description |
|---|---|
| 📊 **Executive Dashboard** | KPI metrics, risk score distribution, DuckDB-powered top-risk queries |
| 🌍 **Live Risk Heatmap** | Scatter-geo world map showing supplier locations colored by risk severity |
| 📡 **Intelligence Feed** | Real-time global disruption news via the GDELT Project API |
| ⚗️ **Scenario Simulator** | What-if analysis: region disruption multiplier, inventory shortfall calculator, lead time projector |
| 📄 **Automated PDF Report** | One-click executive PDF with risk statistics and critical supplier table |
| 🚨 **Anomaly Alerts** | Z-score based statistical anomaly detection with banner alerts |
| 🔌 **Module Status Panel** | Live sidebar showing which modules loaded successfully on Streamlit Cloud |

---

## 🛠️ Tech Stack

| Component | Technology |
|---|---|
| **UI Framework** | [Streamlit](https://streamlit.io) |
| **Data Engine** | [Polars](https://pola.rs) + [DuckDB](https://duckdb.org) |
| **Visualizations** | [Plotly](https://plotly.com/python/) |
| **News Intelligence** | [GDELT Project API](https://www.gdeltproject.org/) (Free) |
| **Weather Alerts** | [OpenWeatherMap API](https://openweathermap.org/api) (Free Tier) |
| **PDF Generation** | [FPDF2](https://py-fpdf2.readthedocs.io/) |
| **Language** | Python 3.11 |
| **Deployment** | Streamlit Community Cloud (Free Tier) |

---

## 📁 Project Structure

```
ROOT/
├── app.py                    ← Main entry point
├── theme.py                  ← Neon/terminal CSS theme + Plotly layout
├── requirements.txt
│
├── engine/
│   ├── ingest.py             ← CSV loader, GDELT fetcher, schema detector
│   ├── news_stream.py        ← Real-time disruption event stream
│   ├── risk_model.py         ← Geo, delay & financial risk scoring
│   └── scenario_sim.py       ← Disruption simulator & inventory calculator
│
├── database/
│   └── risk_queries.py       ← DuckDB in-memory queries
│
├── components/
│   ├── alerts.py             ← Anomaly detection & banner alerts
│   ├── map_viz.py            ← Scatter-geo & choropleth map builders
│   └── views.py              ← Page-level UI components
│
├── utils/
│   └── pdf_gen.py            ← PDF report generator (FPDF2)
│
└── data/
    └── suppliers.csv         ← Sample supplier dataset
```

---

## 🚀 Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/your-username/supply-chain-risk-engine.git
cd supply-chain-risk-engine
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Add API keys (optional)

Create a `.streamlit/secrets.toml` file:

```toml
OPENWEATHER_API_KEY = "your_openweathermap_key_here"
```

> The app runs fully without API keys — weather alerts will be disabled but all other features work normally.

### 4. Run the app

```bash
streamlit run app.py
```

---

## 📄 CSV Format

Upload any CSV with the following columns (column names are **case-insensitive**):

| Column | Required | Aliases Accepted |
|---|---|---|
| `supplier` / `supplier_name` | ✅ Yes | `vendor`, `name`, `company` |
| `risk_score` / `Risk_Score` | ✅ Yes | `risk`, `score`, `rating` |
| `region` / `Supplier_Region` | ⚪ Recommended | `country`, `area`, `zone` |
| `lat` | ⚪ For Map | `latitude`, `y` |
| `lon` | ⚪ For Map | `longitude`, `lng`, `x` |

**Sample row:**
```
supplier_name,Supplier_Region,lat,lon,Risk_Score
Palmer Gray and Williams,MIDDLE_EAST,25.2,55.3,100
```

---

## 🧩 Module Breakdown

### `engine/risk_model.py`
Computes a **composite risk score (0–100)** using three weighted components:

```
Total Risk = (Geo Risk × 0.4) + (Delay Risk × 0.3) + (Financial Risk × 0.3)
```

- **Geo Risk** — logistic curve over event density × regional sensitivity
- **Delay Risk** — lead time volatility model
- **Financial Risk** — log-scaled revenue exposure + supplier health penalty

### `engine/scenario_sim.py`
- `simulate_disruption()` — applies a multiplier to risk scores in affected regions
- `calc_inventory_impact()` — computes days-of-cover and shortfall probability
- `project_lead_time_change()` — models port congestion + labor strike impact

### `database/risk_queries.py`
Runs parameterized SQL via **DuckDB in-memory** engine on top of Polars DataFrames. No external database required.

### `utils/pdf_gen.py`
Auto-detects column names from any CSV schema. Generates a 2-page PDF with executive summary, risk statistics, and a critical supplier table filtered at `risk_score > 50`.

---

## ☁️ Deployment

This app is optimized for **Streamlit Community Cloud (Free Tier)**:

- ✅ In-memory only — no persistent storage required
- ✅ RAM usage stays under 1 GB for typical datasets (< 100k rows)
- ✅ All modules have graceful fallbacks if imports fail on Cloud
- ✅ API keys managed via Streamlit Secrets

To deploy:
1. Push your repo to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your repo and set `app.py` as the entry point
4. Add `OPENWEATHER_API_KEY` under **Secrets** (optional)

---

## 📦 Requirements

```
streamlit==1.31.1
polars==0.20.10
duckdb==0.10.0
plotly==5.18.0
fpdf2==2.7.8
requests==2.31.0
numpy==1.26.4
pillow==10.2.0
```

---

## 📜 License

This project is licensed under the **MIT License** — see [LICENSE](LICENSE) for details.

---

<p align="center">
  Built with ⚡ by <strong>Ali-datasmith</strong> &nbsp;|&nbsp;
  Powered by Streamlit · Polars · DuckDB · Plotly
</p>
