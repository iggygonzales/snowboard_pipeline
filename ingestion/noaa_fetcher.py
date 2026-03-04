import requests
from datetime import datetime
from config.resorts import RESORTS

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

def run():
    print(f"\n🏂 Snow Conditions Report — {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
    print("-" * 50)
    
    for resort in RESORTS:
        print(f"\n📍 {resort['name']}, {resort['state']}")
        try:
            conditions = fetch_conditions(resort["noaa_station"])
            print(f"   Temp:       {conditions['temp_f']}°F")
            print(f"   Wind:       {conditions['wind_speed_mph']} mph")
            print(f"   Conditions: {conditions['conditions']}")
            print(f"   Updated:    {conditions['timestamp']}")
        except Exception as e:
            print(f"   ❌ Error: {e}")

if __name__ == "__main__":
    run()