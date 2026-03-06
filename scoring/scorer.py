import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from storage.db import get_connection

def calculate_ride_score(temp_f, wind_speed_mph, conditions, snowfall_in, rolling_72hr_snowfall=0, freeze_thaw_flag=0):
    score = 50  # baseline

    # --- Temperature score (ideal: 20-32°F) ---
    if temp_f is None:
        temp_score = 0
    elif 20 <= temp_f <= 32:
        temp_score = 25
    elif 10 <= temp_f < 20:
        temp_score = 15
    elif 32 < temp_f <= 40:
        temp_score = 10
    elif temp_f > 40:
        temp_score = -10
    else:
        temp_score = 5

    # --- Wind penalty ---
    if wind_speed_mph is None:
        wind_score = 0
    elif wind_speed_mph <= 10:
        wind_score = 15
    elif wind_speed_mph <= 20:
        wind_score = 0
    elif wind_speed_mph <= 35:
        wind_score = -15
    else:
        wind_score = -30

    # --- Conditions bonus ---
    if conditions is None:
        conditions_score = 0
    else:
        conditions_lower = conditions.lower()
        if "snow" in conditions_lower:
            conditions_score = 15
        elif "clear" in conditions_lower or "sunny" in conditions_lower:
            conditions_score = 10
        elif "cloud" in conditions_lower:
            conditions_score = 5
        elif "fog" in conditions_lower or "mist" in conditions_lower:
            conditions_score = -5
        elif "rain" in conditions_lower or "drizzle" in conditions_lower:
            conditions_score = -20
        else:
            conditions_score = 0

    # --- Rolling 72hr snowfall bonus (fresh snow!) ---
    if rolling_72hr_snowfall and rolling_72hr_snowfall > 0:
        snow_bonus = min(rolling_72hr_snowfall * 5, 20)  # cap at 20pts
    elif snowfall_in and snowfall_in > 0:
        snow_bonus = min(snowfall_in * 10, 10)
    else:
        snow_bonus = 0

    # --- Freeze/thaw penalty (icy conditions) ---
    ice_penalty = -15 if freeze_thaw_flag else 0

    total = score + temp_score + wind_score + conditions_score + snow_bonus + ice_penalty
    return max(0, min(100, total))


def grade(score):
    if score >= 80:
        return "🟢 Excellent"
    elif score >= 65:
        return "🔵 Good"
    elif score >= 50:
        return "🟡 Decent"
    elif score >= 35:
        return "🟠 Poor"
    else:
        return "🔴 Stay Home"


def run():
    con = get_connection()

    # read from features table instead of raw conditions
    results = con.execute("""
        SELECT DISTINCT ON (resort)
            resort,
            state,
            temp_f,
            wind_speed_mph,
            snowfall_in,
            conditions,
            rolling_72hr_snowfall,
            freeze_thaw_flag,
            fetched_at
        FROM features
        ORDER BY resort, fetched_at DESC
    """).fetchall()

    con.close()

    print("\n🏂 Ride Quality Scores\n")
    print(f"{'Resort':<20} {'Temp':>6} {'Wind':>8} {'72hr Snow':>10} {'Ice Risk':>9} {'Score':>7} {'Rating'}")
    print("-" * 85)

    for row in results:
        resort, state, temp_f, wind_mph, snowfall, conds, rolling_snow, freeze_thaw, ts = row
        score = calculate_ride_score(temp_f, wind_mph, conds, snowfall, rolling_snow, freeze_thaw)
        rating = grade(score)
        ice = "⚠️ Yes" if freeze_thaw else "No"
        temp_str = f"{round(temp_f, 1)}°F"
        wind_str = f"{round(wind_mph, 1)}mph"
        snow_str = f"{round(rolling_snow or 0, 2)}in"
        print(f"{resort + ', ' + state:<20} {temp_str:>8} {wind_str:>8} {snow_str:>10} {ice:>9} {score:>7} {rating}")


if __name__ == "__main__":
    run()