# 🏂 New England Snowboard Conditions Pipeline

A real-time AI-powered data pipeline that fetches, stores, transforms, and scores snowboarding conditions across 6 New England resorts using live NOAA weather data. Features a Claude AI chatbot that gives personalized resort recommendations based on live conditions.

**Live at:** http://18.119.236.205:8501

## Overview

This project ingests hourly weather data from the NOAA API, stores it in a DuckDB database, runs dbt transformations to engineer features, applies a custom ride quality scoring model, and surfaces everything in a Streamlit dashboard with an AI chatbot layer — all running 24/7 on AWS EC2 with Prefect orchestration.

## UI

<img width="2397" height="472" alt="snow1" src="https://github.com/user-attachments/assets/a948d816-7efe-49e1-ba88-964e73182837" />

<img width="2171" height="942" alt="snow2" src="https://github.com/user-attachments/assets/ffc93e25-4e71-4bbd-a58c-e2682af7058e" />

<img width="2288" height="620" alt="snow3" src="https://github.com/user-attachments/assets/7deea231-075a-43e9-ad7a-66c766a521de" />

## Demo

<img width="1920" height="1080" alt="Adobe Express - Video Project 0 (1)" src="https://github.com/user-attachments/assets/b6a106d8-add0-44f1-816a-618158d428f7" />

## Resorts Tracked

| Resort | State | NOAA Station |
|---|---|---|
| Stowe | VT | KMVL |
| Killington | VT | KRUT |
| Loon Mountain | NH | KLEB |
| Sugarloaf | ME | KAUG |
| Sunday River | ME | KIZG |
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
                         AWS EC2 (Docker + GitHub Actions CI/CD)
```

## Features

**Dashboard**
- Live resort leaderboard ranked by ride quality score
- Resort detail cards with temperature, wind, and conditions
- Freeze/thaw ice risk warnings
- Score history chart showing trends over time (Plotly)
- Timestamps displayed in EST
- Off-season detection — scores return 0 outside of November–April

**7-Day Forecast**
- NOAA forecast API integration for predictive scoring
- Per-resort 7-day forecast cards with temperature, wind, and conditions
- Predicted ride quality score for each forecast day
- Temperature chart with freezing line indicator
- Detailed forecast expander per period

**AI Snow Bot**
- Powered by Claude Sonnet via the Anthropic API
- Reads live conditions data and ride quality scores
- Gives personalized resort recommendations in natural language
- Maintains conversation context across multiple questions

## Scoring Model

Each resort receives a ride quality score from 0–100 based on:

- **Off-season check** — scores return 0 outside of November–April
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
| 0 (off-season) | ⚪ Offseason |

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
| CI/CD | GitHub Actions (auto-deploy on push to main) |

## Project Structure

```
snowboard-pipeline/
├── config/
│   └── resorts.py              # Resort + NOAA station config + coordinates
├── ingestion/
│   ├── noaa_fetcher.py         # Hourly NOAA conditions ingestion
│   └── noaa_forecast.py        # 7-day NOAA forecast ingestion
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
├── .github/
│   └── workflows/
│       └── deploy.yml          # GitHub Actions CI/CD workflow
├── data/                       # DuckDB database (gitignored)
├── logs/                       # Pipeline logs (gitignored)
├── Dockerfile
├── deploy.sh                   # One-command EC2 deploy script
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

**3. Run the conditions fetcher:**
```bash
python -m ingestion.noaa_fetcher
```

**4. Run dbt transforms:**
```bash
cd transforms/snow_transforms
dbt run
```

**5. Run the forecast fetcher:**
```bash
python -m ingestion.noaa_forecast
```

**6. Launch the dashboard:**
```bash
streamlit run dashboard/app.py
```

**7. Run the full Prefect flow manually:**
```bash
python -m orchestration.pipeline_flow
```

**8. Run with Docker:**
```bash
docker build -t snowboard-pipeline .
docker run -p 8501:8501 \
  --env-file .env \
  snowboard-pipeline
```

## AWS Deployment

The pipeline runs on an AWS EC2 t2.micro instance (free tier) with an Elastic IP at `18.119.236.205`.

**SSH into EC2:**
```bash
ssh -i "snowboard-key.pem" ec2-user@18.119.236.205
```

**CI/CD — auto-deploy on push:**

Every push to `main` triggers a GitHub Actions workflow that SSHs into EC2, pulls the latest code, and rebuilds the Docker container automatically.

**Check container status:**
```bash
docker ps
docker logs -f snowboard-pipeline
```

## Roadmap

- [x] NOAA forecast API integration for 7-day predictive scoring
- [ ] Expand to national resort coverage
- [ ] Spark processing layer for scale
- [ ] Resort snow report scraping for deeper condition data