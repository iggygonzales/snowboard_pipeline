import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import requests
from datetime import datetime
from config.resorts import RESORTS
from storage.db import get_connection

POINTS_URL = "https://api.weather.gov/points/{lat},{lon}"
HEADERS = {"User-Agent": "snowboard-pipeline (your@email.com)"}


def get_forecast_url(lat, lon):
    """Get the forecast grid URL for a lat/lon from NOAA points API."""
    url = POINTS_URL.format(lat=lat, lon=lon)
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()
    return response.json()["properties"]["forecast"]


def fetch_forecast(lat, lon):
    """Fetch 7-day forecast periods for a lat/lon."""
    forecast_url = get_forecast_url(lat, lon)
    response = requests.get(forecast_url, headers=HEADERS)
    response.raise_for_status()
    periods = response.json()["properties"]["periods"]
    return periods[:14]  # 14 periods = 7 days (day + night each)


def save_forecast(resort, periods):
    """Save forecast periods to the forecasts table."""
    con = get_connection()
    # Clear old forecasts for this resort before inserting new ones
    con.execute("DELETE FROM forecasts WHERE resort = ?", [resort["name"]])
    for period in periods:
        con.execute("""
            INSERT INTO forecasts (
                resort, state, period_name, start_time, end_time,
                is_daytime, temp_f, wind_speed, wind_direction,
                short_forecast, detailed_forecast, fetched_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, [
            resort["name"],
            resort["state"],
            period["name"],
            period["startTime"],
            period["endTime"],
            period["isDaytime"],
            period["temperature"],
            period["windSpeed"],
            period["windDirection"],
            period["shortForecast"],
            period["detailedForecast"],
            datetime.utcnow().isoformat(),
        ])
    con.close()


def run():
    print(f"\n🔮 Forecast Fetch — {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
    print("-" * 50)

    for resort in RESORTS:
        print(f"\n {resort['name']}, {resort['state']}")
        try:
            periods = fetch_forecast(resort["lat"], resort["lon"])
            save_forecast(resort, periods)
            print(f"   Saved {len(periods)} forecast periods")
        except Exception as e:
            print(f"   Error: {e}")


if __name__ == "__main__":
    run()