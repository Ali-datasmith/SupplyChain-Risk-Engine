<img width="1024" height="254" alt="image" src="https://github.com/user-attachments/assets/8a5ba33b-4234-45b6-9930-b1b43ee2051b" />

# SupplyChain-Risk-Engine

![CI](https://github.com/Ali-datasmith/SupplyChain-Risk-Engine/actions/workflows/ci.yml/badge.svg) ![Python](https://img.shields.io/badge/python-3.12%20%7C%203.13-3776AB?logo=python&logoColor=white) ![Streamlit](https://img.shields.io/badge/streamlit-1.31-FF4B4B?logo=streamlit&logoColor=white) ![Polars](https://img.shields.io/badge/polars-0.20-CD792C) ![DuckDB](https://img.shields.io/badge/duckdb-0.10-FFF000) ![Tests](https://img.shields.io/badge/tests-20%20passed-brightgreen) ![License](https://img.shields.io/badge/license-MIT-00FF41)

CI passing on Python 3.12 / 3.13 · 20/20 tests green · MIT

## Overview

SupplyChain-Risk-Engine ingests supplier CSVs, computes a weighted geo/delay/financial risk score per supplier, simulates disruption scenarios, and exports executive PDF reports. The compute layer is Polars and DuckDB; the interface is Streamlit. The application runs with no authentication and no required API keys.

## Demo Walkthrough

<!-- LOOM PLACEHOLDER: replace the URL below with your Loom share link -->
[▶ Watch the 1-minute walkthrough on Loom](https://github.com/user-attachments/assets/2c5fe4c4-2282-4dc2-afbf-910ad79e8a28)

Live instance: [supplychain-risk-engine-r8djbttt6eah48khhsfcze.streamlit.app](https://supplychain-risk-engine-hkgbn3bguljkjbrdxhnkyl.streamlit.app/)

## Tech Stack

| Layer | Technology | Why |
|---|---|---|
| Data processing | Polars | Primary dataframe engine for CSV ingestion and transforms |
| Analytics | DuckDB | In-process SQL for dashboard and Top-10 supplier queries |
| UI | Streamlit | Single-file app framework, deployable to Streamlit Community Cloud |
| Visualization | Plotly | Scatter-geo heatmap and scenario/weather charts |
| Reporting | FPDF2 | Executive PDF generation with column auto-detection |
| HTTP | Requests | RSS feed retrieval and Open-Meteo API calls |
| Numerics | NumPy | Z-score anomaly detection and risk math |
| Imaging | Pillow | Image handling for report/UI assets |

## Features

### Executive Risk Dashboard
KPIs, a risk histogram, Z-score anomaly detection, and a Top-10 riskiest suppliers view backed by live DuckDB SQL.

### Global Risk Heatmap
Plotly scatter-geo map; marker size and color scale with supplier risk score.

### Intelligence Feed
Aggregates 8 RSS sources — Supply Chain Dive, Logistics Management, FreightWaves, DC Velocity, JOC, Hellenic Shipping News, Reuters Trade, Bloomberg Supply Chain. Keyword search and source filters. No API keys.

### Scenario Lab
Region disruption multiplier (1–5x) with a baseline-vs-simulated chart. Computes inventory days-of-cover, shortfall probability, and lead-time projection from a port congestion index and labor strike input.

### Weather Monitor
Open-Meteo integration (free, no key). Current conditions, LOW→SEVERE shipping risk classification, 24-hour wind and precipitation charts.

### PDF Report
One-click FPDF2 executive report with flexible column auto-detection across CSV schema variants.

### Platform Behavior
Zero-auth public demo. Neon terminal theme. Graceful module fallbacks on cold start.

## Risk Scoring Model

| Component | Methodology | Weight |
|---|---|---|
| Geo Risk | Geographic exposure score | 40% |
| Delay Risk | Delivery/lead-time risk score | 30% |
| Financial Risk | Financial stability score | 30% |

`Total Risk = (Geo × 0.40) + (Delay × 0.30) + (Financial × 0.30)`

| Tier | Score Range |
|---|---|
| LOW | 0–25 |
| MEDIUM | 26–50 |
| HIGH | 51–75 |
| CRITICAL | 76–100 |

## Architecture

```text
SupplyChain-Risk-Engine/
├── app.py
├── theme.py
├── pyproject.toml
├── requirements.txt
├── requirements-dev.txt
├── tests/
├── engine/
│   ├── ingest.py
│   ├── news_stream.py
│   ├── risk_model.py
│   └── scenario_sim.py
├── database/
│   └── risk_queries.py
├── components/
│   ├── alerts.py
│   ├── map_viz.py
│   └── views.py
├── utils/
│   └── pdf_gen.py
└── data/
```

## Quickstart

Clone the repository:

```bash
git clone https://github.com/Ali-datasmith/SupplyChain-Risk-Engine.git
cd SupplyChain-Risk-Engine
```

Install dependencies and run the app:

```bash
pip install -r requirements.txt
streamlit run app.py
```

## CSV Contract

| Field | Requirement | Accepted aliases |
|---|---|---|
| `supplier` | Required | `supplier_name`, `vendor`, `name` |
| `risk_score` | Required | `risk`, `score`, `rating` |
| `region` | Recommended | `country`, `area`, `zone` |
| `lat` | Required for map pages | `latitude`, `y` |
| `lon` | Required for map pages | `longitude`, `lng`, `x` |

## Testing & CI

```bash
pip install -r requirements-dev.txt
pytest
```

Run a single test file:

```bash
pytest tests/test_risk_model.py -v
```

The suite contains 20 unit tests across 5 modules: `risk_model`, `scenario_sim`, `alerts`, `risk_queries`, `pdf_gen`. The Streamlit runtime is mocked in `tests/conftest.py` using `pytest-mock` and `pyarrow`, installed via `requirements-dev.txt` with Python-version markers.

CI is defined in `.github/workflows/ci.yml` and runs on a 3.12 / 3.13 matrix on every push and pull request.

## Deployment

Runs on Streamlit Community Cloud's free tier: in-memory only, no API keys, under 1 GB RAM at 100k rows.

## Roadmap (V2 — planned, not in V1)

- Pydantic input validation
- Pandera data quality gates
- Loguru structured logging
- GenAI-generated headline summaries for the Intelligence Feed

## License

MIT

## Contact

Ali-datasmith
Email: [rjptmhmmd@gmail.com](mailto:rjptmhmmd@gmail.com)
