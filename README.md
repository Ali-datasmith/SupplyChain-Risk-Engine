# 🛡️ Global Supply Chain Risk Engine

<div align="center">

![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-1.31-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)
![Polars](https://img.shields.io/badge/Polars-0.20-CD792C?style=for-the-badge&logo=polars&logoColor=white)
![DuckDB](https://img.shields.io/badge/DuckDB-0.10-FFF000?style=for-the-badge&logo=duckdb&logoColor=black)
![Plotly](https://img.shields.io/badge/Plotly-5.18-3F4F75?style=for-the-badge&logo=plotly&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-00FF41?style=for-the-badge)

**A real-time, enterprise-grade supply chain risk monitoring platform — built entirely with open-source Python tools, deployed on the cloud, and protected with secure authentication.**

[🚀 Live Demo](https://your-app.streamlit.app) &nbsp;•&nbsp; [📂 Repository](https://github.com/Ali-datasmith/SupplyChain-Risk-Engine)

</div>

---

## 📸 Application Preview

<!-- ============================================================
     EDIT ZONE 1 — Paste your login screen screenshot below
     Example: ![Login Screen](assets/login.png)
     ============================================================ -->

> 🖼️ **[ PASTE LOGIN SCREEN SCREENSHOT HERE ]**

---

## 🎬 Full Demo

<!-- ============================================================
     EDIT ZONE 2 — Paste your demo video or GIF below
     YouTube: [![Watch Demo](assets/thumb.png)](https://youtube.com/your-link)
     GIF:     ![Demo](assets/demo.gif)
     ============================================================ -->

> 🎥 **[ PASTE DEMO VIDEO / GIF HERE ]**

---

## 💡 What Is This?

The **Global Supply Chain Risk Engine** is a full-stack data intelligence platform that helps procurement teams, logistics managers, and risk analysts **identify, monitor, and simulate supply chain disruptions — before they happen.**

Unlike generic BI dashboards, this engine combines:

- **Real-time news intelligence** from 8 industry-specific RSS feeds
- **Live weather risk scoring** along shipping routes via Open-Meteo
- **Dynamic risk modeling** using financial, geopolitical, and delay factors
- **What-if scenario simulation** for disruption planning
- **One-click PDF audit reports** for executive stakeholders
- **Secure SHA-256 login system** — no plain-text passwords, ever

All of this runs on **Streamlit Community Cloud — completely free to host.**

---

## ✨ Feature Breakdown

### 🔐 Secure Access Terminal
A professional neon-themed login screen protects the entire application. Credentials are SHA-256 hashed with a cryptographic salt. No plain-text passwords stored anywhere in the codebase. Built for single-tenant or multi-client deployment.

### 📊 Executive Risk Dashboard
The command center of the application. Upload any supplier CSV and instantly see:

- Average risk score across your entire supplier network
- Count of high-risk suppliers (score > 75)
- Statistical anomaly detection via Z-score analysis
- Risk score distribution histogram
- Top 10 highest-risk suppliers via live DuckDB SQL query

### 🌍 Global Risk Heatmap
An interactive Plotly scatter-geo world map that plots every supplier by geographic coordinates, sized and colored by risk score. Instantly visualize where your supply chain is most exposed — from APAC manufacturing hubs to Middle East trade corridors.

### 📡 Supply Chain Intelligence Feed
Live news pulled from 8 industry-specific RSS sources — zero API keys required:

| Source | Coverage |
|---|---|
| Supply Chain Dive | Industry operations & disruptions |
| Logistics Management | Warehousing, freight, 3PL |
| FreightWaves | Freight markets & trucking |
| DC Velocity | Distribution & materials handling |
| JOC | Port & container shipping |
| Hellenic Shipping News | Global maritime intelligence |
| Reuters Trade | Global trade & commerce |
| Bloomberg Supply Chain | Financial & market risk |

Filter by source, search by keyword (`tariff`, `port strike`, `logistics`), and read full articles directly from the dashboard in expandable cards.

### ⚗️ Risk Scenario Simulator
A three-part what-if analysis engine for proactive risk planning:

**Region Disruption Simulator** — Select any region and apply a disruption intensity multiplier (1x–5x). See a live bar chart comparing baseline vs simulated risk scores across your entire supplier network.

**Inventory Impact Calculator** — Input current stock, daily demand, and lead time to compute days-of-cover and shortfall probability with a color-coded risk banner.

**Lead Time Projector** — Model the combined effect of port congestion index and active labor strikes on expected delivery timelines.

### 🌦️ Shipping Route Weather Monitor
Powered by Open-Meteo — completely free, no API key, no credit card. Select any supplier from your dataset and get:

- Current temperature, wind speed, and precipitation probability
- Shipping risk classification: 🟢 LOW → 🟡 MODERATE → 🟠 HIGH → 🔴 SEVERE
- 24-hour wind speed forecast (line chart)
- 24-hour precipitation probability (color-coded bar chart)

### 📄 Automated PDF Risk Report
One-click generation of a professional audit-ready PDF containing:

- Customizable executive summary
- Risk statistics (average, min, max scores across all suppliers)
- Critical supplier table (auto-filtered at risk score > 50)
- Auto-detects column names from any CSV schema — no manual mapping

---

## 🧠 Risk Scoring Model

Each supplier receives a **composite risk score (0–100)** from three weighted components:

```
Total Risk = (Geo Risk × 0.40) + (Delay Risk × 0.30) + (Financial Risk × 0.30)
```

| Component | Methodology | Weight |
|---|---|---|
| **Geo Risk** | Logistic growth curve over event density × regional sensitivity coefficient | 40% |
| **Delay Risk** | Lead time volatility model: avg delay days + historical variance | 30% |
| **Financial Risk** | Log-scaled revenue exposure + supplier health penalty (1 − rating) | 30% |

Scores normalize to 0–100 via Min-Max scaling and classify into tiers:
`LOW (0–25)` → `MEDIUM (26–50)` → `HIGH (51–75)` → `CRITICAL (76–100)`

---

## 🏗️ Project Architecture

```
ROOT/
├── app.py                    ← Main entry point + SHA-256 login gate
├── theme.py                  ← Neon/terminal CSS theme + Plotly dark layout
├── requirements.txt
│
├── engine/
│   ├── ingest.py             ← CSV loader, schema auto-detection, GDELT
│   ├── news_stream.py        ← RSS intelligence feed + Open-Meteo weather
│   ├── risk_model.py         ← Geo, delay & financial risk scoring engine
│   └── scenario_sim.py       ← Disruption simulator, inventory & lead time calc
│
├── database/
│   └── risk_queries.py       ← DuckDB in-memory SQL analytics layer
│
├── components/
│   ├── alerts.py             ← Z-score anomaly detection & alert banners
│   ├── map_viz.py            ← Scatter-geo & choropleth map builders
│   └── views.py              ← Page-level UI components
│
├── utils/
│   └── pdf_gen.py            ← FPDF2 professional report generator
│
└── data/
    └── suppliers.csv         ← Sample dataset (50 global suppliers)
```

---

## 🛠️ Tech Stack

| Layer | Technology | Reason |
|---|---|---|
| **UI & Hosting** | Streamlit 1.31 | Rapid deployment, free cloud tier |
| **Data Engine** | Polars 0.20 | 10–100x faster than Pandas on large CSVs |
| **Analytics** | DuckDB 0.10 | In-memory SQL on DataFrames, zero setup |
| **Visualization** | Plotly 5.18 | Interactive geo maps, charts, hover tooltips |
| **News Feed** | RSS feeds (8 sources) | Free, reliable, no API key required |
| **Weather** | Open-Meteo API | 100% free, no registration needed |
| **PDF Export** | FPDF2 2.7 | Lightweight professional PDF generation |
| **Security** | SHA-256 + Salt | Industry-standard password hashing |

---

## 🚀 Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/Ali-datasmith/SupplyChain-Risk-Engine.git
cd SupplyChain-Risk-Engine
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Run locally

```bash
streamlit run app.py
```

### 4. Login

```
Username : Ali-datasmith
Password : Contact the developer
```

---

## 📄 CSV Format

The engine accepts **any CSV format** — column names are auto-detected and normalized at upload time:

| Column | Required | Accepted Aliases |
|---|---|---|
| `supplier` | ✅ Yes | `supplier_name`, `vendor`, `name`, `company` |
| `risk_score` | ✅ Yes | `Risk_Score`, `risk`, `score`, `rating` |
| `region` | ⭐ Recommended | `Supplier_Region`, `country`, `area`, `zone` |
| `lat` | 🗺️ Map only | `latitude`, `y` |
| `lon` | 🗺️ Map only | `longitude`, `lng`, `x` |

Extra columns (`industry`, `lead_time_days`, `financial_score`, `reliability_score`, `inventory_value`) are automatically used where applicable.

---

## 💼 Real-World Use Cases

**Procurement Teams** — Identify which suppliers pose the highest risk before contract renewal. Prioritize audits based on data, not gut feeling.

**Logistics Managers** — Monitor live weather risk along shipping routes. Get early warnings before a typhoon or port strike disrupts your network.

**Risk & Compliance Officers** — Generate audit-ready PDF reports with one click. Present executive summaries to leadership without manual data preparation.

**Investment Analysts** — Model supply chain exposure for portfolio companies. Run what-if scenarios on geopolitical disruptions — Red Sea conflict, China tariffs, labor strikes.

**Consulting Firms** — White-label this platform for clients. Deploy a branded version within hours with custom supplier datasets.

---

## 📈 Growth Roadmap

The modular architecture makes the following extensions straightforward:

- **Multi-tenant SaaS** — Per-client login with isolated data views
- **ERP Integration** — Connect to SAP, Oracle, or NetSuite via REST API
- **ML Risk Prediction** — Train a gradient boosting model on historical disruptions
- **Real-time Alerts** — Email/Slack notifications when risk scores cross thresholds
- **Supplier Benchmarking** — Peer comparison within same region or industry
- **Mobile Responsive UI** — Progressive Web App for field use

---

## ☁️ Deployment

Optimized for **Streamlit Community Cloud (Free Tier)**:

- ✅ In-memory only — no persistent database or file system needed
- ✅ All modules have graceful fallbacks if imports fail on cold start
- ✅ RAM usage stays under 1 GB for datasets up to 100,000 rows
- ✅ No API keys required for any core feature

```
1. Push repository to GitHub
2. Go to share.streamlit.io
3. Connect repository → set app.py as entry point
4. Click Deploy — live in 60 seconds
```

---

## 📦 Dependencies

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

## 👨‍💻 About the Developer

Built by **Ali-datasmith** — a data engineer specializing in supply chain analytics, real-time intelligence dashboards, and Python-based risk platforms.

**Open to:**
- Freelance projects — Upwork / Direct contract
- Consulting engagements for logistics & procurement firms
- Full-time Data Engineering / Analytics Engineering roles

📧 rjptmhmmd@gmail.com
🔗 [GitHub Profile](https://github.com/Ali-datasmith)

---

## 📜 License

MIT License — free to use, modify, and distribute with attribution.

---

<div align="center">

**⚡ Built by Ali-datasmith**

*Polars · DuckDB · Streamlit · Plotly · Open-Meteo · FPDF2*

*"From raw supplier data to executive risk intelligence — in seconds."*

</div>
