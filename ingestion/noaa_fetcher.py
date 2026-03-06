import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import requests
from datetime import datetime
from config.resorts import RESORTS
from storage.db import get_connection, initialize_db

BASE_URL = "https://api.weather.gov/stations/{station}/observations/latest"

def celsius_to_f(c):
    if c is None:
        return None
    return round((c * 9/5) + 32, 1)

def ms_to_mph(ms):
    if ms is None:
        return None
    return round(ms * 2.237, 1)

def fetch_conditions(station_id: str) -> dict:
    url = BASE_URL.format(station=station_id)
    headers = {"User-Agent": "snowboard-pipeline (your@email.com)"}
    
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    
    data = response.json()
    props = data["properties"]
    
    return {
        "timestamp": props["timestamp"],
        "temp_f": celsius_to_f(props["temperature"]["value"]),
        "wind_speed_mph": ms_to_mph(props["windSpeed"]["value"]),
        "snowfall_in": props.get("snowfallSinceLastObservation", {}).get("value"),
        "visibility_m": props["visibility"]["value"],
        "conditions": props["textDescription"],
    }

def save_conditions(resort: dict, conditions: dict):
    con = get_connection()
    con.execute("""
        INSERT INTO conditions (
            resort, state, timestamp, temp_f,
            wind_speed_mph, snowfall_in, visibility_m, conditions
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, [
        resort["name"],
        resort["state"],
        conditions["timestamp"],
        conditions["temp_f"],
        conditions["wind_speed_mph"],
        conditions["snowfall_in"],
        conditions["visibility_m"],
        conditions["conditions"],
    ])
    con.close()

def run():
    initialize_db()
    print(f"\n🏂 Snow Conditions Report — {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
    print("-" * 50)
    
    for resort in RESORTS:
        print(f"\n📍 {resort['name']}, {resort['state']}")
        try:
            conditions = fetch_conditions(resort["noaa_station"])
            save_conditions(resort, conditions)
            print(f"   Temp:       {conditions['temp_f']}°F")
            print(f"   Wind:       {conditions['wind_speed_mph']} mph")
            print(f"   Conditions: {conditions['conditions']}")
            print(f"   Updated:    {conditions['timestamp']}")
            print(f"   ✅ Saved to database")
        except Exception as e:
            print(f"   ❌ Error: {e}")

if __name__ == "__main__":
    run()