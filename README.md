# 🏂 New England Snowboard Conditions Pipeline

A real-time data pipeline that fetches, stores, transforms, and scores snowboarding conditions across 6 New England resorts using live NOAA weather data. Deployed on AWS EC2 and accessible at http://52.14.162.178:8501

## Overview

This project ingests hourly weather data from the NOAA API, stores it in a DuckDB database, runs dbt transformations to engineer features, applies a custom ride quality scoring model, and surfaces everything in a Streamlit dashboard — all running 24/7 on AWS EC2.

## Resorts Tracked

| Resort | State | NOAA Station |
|---|---|---|
| Stowe | VT | KSFM |
| Killington | VT | KRUT |
| Loon Mountain | NH | KLCI |
| Sugarloaf | ME | KBHB |
| Sunday River | ME | KBGR |
| Wachusett | MA | KORH |

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
                        Streamlit Dashboard (AWS EC2)
```

## Scoring Model

Each resort receives a ride quality score from 0–100 based on:

- **Temperature** — ideal range 20–32°F
- **Wind speed** — penalized above 20mph, heavily penalized above 35mph
- **Conditions** — bonus for snow, penalty for rain/fog
- **Rolling 72hr snowfall** — fresh snow bonus (capped at 20pts)
- **Freeze/thaw detection** — 15pt ice risk penalty when temps cross freezing threshold

Scores are graded as Excellent / Good / Decent / Poor / Stay Home. Ice warnings are displayed on the dashboard when freeze/thaw is detected.

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
| Orchestration | Cron (AWS EC2) |
| Cloud | AWS EC2 + Elastic IP |

## Project Structure
```
snowboard-pipeline/
├── config/
│   └── resorts.py              # Resort + NOAA station config
├── ingestion/
│   └── noaa_fetcher.py         # Hourly NOAA data ingestion
├── storage/
│   └── db.py                   # DuckDB connection + schema
├── scoring/
│   └── scorer.py               # Ride quality scoring model
├── dashboard/
│   └── app.py                  # Streamlit dashboard
├── transforms/
│   └── snow_transforms/        # dbt project
│       └── models/
│           ├── rolling_snowfall.sql
│           ├── freeze_thaw.sql
│           ├── features.sql
│           └── sources.yml
├── data/                       # DuckDB database (gitignored)
├── logs/                       # Pipeline logs (gitignored)
├── Dockerfile
├── deploy.sh                   # One-command EC2 deploy script
├── run_fetcher.bat              # Windows local scheduler script
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

## AWS Deployment

The pipeline runs on an AWS EC2 t2.micro instance (free tier) with an Elastic IP.

**SSH into EC2:**
```bash
ssh -i "snowboard-key.pem" ec2-user@52.14.162.178
```

**Deploy latest changes:**
```bash
./deploy.sh
```

**Cron schedule (runs automatically on EC2):**
```
0 * * * * python3 -m ingestion.noaa_fetcher    # fetch hourly
5 * * * * dbt run                               # rebuild features
```

## Roadmap

- [ ] Natural language chatbot interface powered by Claude API
- [ ] Expand to national resort coverage
- [ ] Airflow orchestration as pipeline complexity grows
- [ ] Spark processing layer for scale
- [ ] Resort snow report scraping for deeper condition data