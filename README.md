# 🏂 New England Snowboard Conditions Pipeline

A real-time data pipeline that fetches, stores, transforms, and scores snowboarding conditions across 6 New England resorts using live NOAA weather data.

## Overview

This project ingests hourly weather data from the NOAA API, stores it in a DuckDB database, runs dbt transformations to engineer features, applies a custom ride quality scoring model, and surfaces everything in a Streamlit dashboard.

## Resorts Tracked

| Resort | State |
|---|---|
| Stowe | VT |
| Killington | VT |
| Loon Mountain | NH |
| Sugarloaf | ME |
| Sunday River | ME |
| Wachusett | MA |

## Architecture
```
NOAA API → Python Ingestion → DuckDB (raw)
                                    ↓
                            dbt Transforms
                                    ↓
                         Feature Tables (DuckDB)
                                    ↓
                         Scoring Model (Python)
                                    ↓
                        Streamlit Dashboard
```

## Scoring Model

Each resort receives a ride quality score from 0–100 based on:

- **Temperature** — ideal range 20–32°F
- **Wind speed** — penalized above 20mph, heavily penalized above 35mph
- **Conditions** — bonus for snow, penalty for rain/fog
- **Rolling 72hr snowfall** — fresh snow bonus
- **Freeze/thaw detection** — ice risk penalty when temps cross freezing threshold

Scores are graded as Excellent / Good / Decent / Poor / Stay Home.

## dbt Models

| Model | Description |
|---|---|
| `rolling_snowfall` | 72-hour rolling snowfall sum per resort |
| `freeze_thaw` | Daily freeze/thaw cycle detection |
| `features` | Combined feature table consumed by scorer |

## Tech Stack

| Layer | Tool |
|---|---|
| Ingestion | Python + NOAA Weather API |
| Storage | DuckDB |
| Transformation | dbt (dbt-duckdb) |
| Scoring | Python (weighted scoring function) |
| Dashboard | Streamlit + Plotly |
| Containerization | Docker |
| Orchestration | Windows Task Scheduler (local) / Cron (AWS) |
| Cloud | AWS EC2 |

## Project Structure
```
snowboard-pipeline/
├── config/
│   └── resorts.py          # Resort + NOAA station config
├── ingestion/
│   └── noaa_fetcher.py     # Hourly NOAA data ingestion
├── storage/
│   └── db.py               # DuckDB connection + schema
├── scoring/
│   └── scorer.py           # Ride quality scoring model
├── dashboard/
│   └── app.py              # Streamlit dashboard
├── transforms/
│   └── snow_transforms/    # dbt project
│       └── models/
│           ├── rolling_snowfall.sql
│           ├── freeze_thaw.sql
│           ├── features.sql
│           └── sources.yml
├── data/                   # DuckDB database (gitignored)
├── logs/                   # Pipeline logs (gitignored)
├── Dockerfile
├── run_fetcher.bat          # Windows scheduler script
└── requirements.txt
```

## Running Locally

**1. Clone the repo and set up venv:**
```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

**2. Run the fetcher:**
```bash
python -m ingestion.noaa_fetcher
```

**3. Run dbt transforms:**
```bash
cd transforms/snow_transforms
dbt run
```

**4. Launch the dashboard:**
```bash
streamlit run dashboard/app.py
```

**5. Run with Docker:**
```bash
docker build -t snowboard-pipeline .
docker run -p 8501:8501 -v $(pwd)/data:/app/data snowboard-pipeline
```

## Future Improvements

- Expand to national resort coverage (Spark processing layer)
- Add Airflow for pipeline orchestration as complexity grows
- Natural language chatbot interface powered by Claude API
- Resort snow report scraping for deeper condition data
- AWS deployment for always-on pipeline
```

---

Commit it:
```
git add .
git commit -m "docs: add README"