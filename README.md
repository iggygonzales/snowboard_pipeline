# 🏂 New England Snowboard Conditions Pipeline

A real-time AI-powered data pipeline that fetches, stores, transforms, and scores snowboarding conditions across 6 New England resorts using live NOAA weather data. Features a Claude AI chatbot that gives personalized resort recommendations based on live conditions.

**Live at:** http://52.14.162.178:8501

## Overview

This project ingests hourly weather data from the NOAA API, stores it in a DuckDB database, runs dbt transformations to engineer features, applies a custom ride quality scoring model, and surfaces everything in a Streamlit dashboard with an AI chatbot layer — all running 24/7 on AWS EC2 with Prefect orchestration.

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
                     Streamlit Dashboard + Claude AI Chatbot
                                    ↓
                         AWS EC2 (Docker + Prefect)
```

## Features

**Dashboard**
- Live resort leaderboard ranked by ride quality score
- Resort detail cards with temperature, wind, and conditions
- Freeze/thaw ice risk warnings
- Score history chart showing trends over time (Plotly)
- Timestamps displayed in EST

**AI Snow Bot**
- Powered by Claude Sonnet via the Anthropic API
- Reads live conditions data and ride quality scores
- Gives personalized resort recommendations in natural language
- Maintains conversation context across multiple questions

## Scoring Model

Each resort receives a ride quality score from 0–100 based on:

- **Temperature** — ideal range 20–32°F
- **Wind speed** — penalized above 20mph, heavily penalized above 35mph
- **Conditions** — bonus for snow, penalty for rain/fog
- **Rolling 72hr snowfall** — fresh snow bonus (capped at 20pts)
- **Freeze/thaw detection** — 15pt ice risk penalty when temps cross freezing threshold

| Score | Rating |
|---|---|
| 80–100 | 🟢 Excellent |
| 65–79 | 🔵 Good |
| 50–64 | 🟡 Decent |
| 35–49 | 🟠 Poor |
| 0–34 | 🔴 Stay Home |

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
| Orchestration | Prefect (hourly schedule, retries, monitoring) |
| Dashboard | Streamlit + Plotly |
| AI Chatbot | Claude Sonnet (Anthropic API) |
| Containerization | Docker |
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
│   └── app.py                  # Streamlit dashboard + AI chatbot
├── orchestration/
│   └── pipeline_flow.py        # Prefect flow with hourly schedule
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

**2. Add your Anthropic API key to `.env`:**
```
ANTHROPIC_API_KEY=your-key-here
```

**3. Run the fetcher:**
```bash
python -m ingestion.noaa_fetcher
```

**4. Run dbt transforms:**
```bash
cd transforms/snow_transforms
dbt run
```

**5. Launch the dashboard:**
```bash
streamlit run dashboard/app.py
```

**6. Run the Prefect flow manually:**
```bash
python -m orchestration.pipeline_flow
```

**7. Run with Docker:**
```bash
docker build -t snowboard-pipeline .
docker run -p 8501:8501 \
  -v $(pwd)/data:/app/data \
  -e ANTHROPIC_API_KEY=your-key-here \
  snowboard-pipeline
```

## AWS Deployment

The pipeline runs on an AWS EC2 t2.micro instance (free tier) with an Elastic IP at `52.14.162.178`.

**SSH into EC2:**
```bash
ssh -i "snowboard-key.pem" ec2-user@52.14.162.178
```

**Deploy latest changes:**
```bash
bash deploy.sh
```

**Prefect orchestration (runs automatically on EC2):**
- Managed by systemd — starts automatically on EC2 reboot
- Hourly schedule via Prefect Cloud
- Automatic retries: 3x on fetch, 2x on dbt
- Monitor runs at app.prefect.cloud

**Check Prefect service status:**
```bash
sudo systemctl status prefect-pipeline
```

**Restart Prefect service:**
```bash
sudo systemctl restart prefect-pipeline
```

## Roadmap

- [ ] NOAA forecast API integration for 7-day predictive scoring
- [ ] Expand to national resort coverage
- [ ] Spark processing layer for scale
- [ ] Resort snow report scraping for deeper condition data