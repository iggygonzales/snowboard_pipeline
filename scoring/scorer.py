from storage.db import get_connection

def calculate_ride_score(temp_f, wind_speed_mph, conditions, snowfall_in):
    score = 50  # baseline

    # --- Temperature score (ideal: 20-32°F) ---
    if temp_f is None:
        temp_score = 0
    elif 20 <= temp_f <= 32:
        temp_score = 25  # perfect range
    elif 10 <= temp_f < 20:
        temp_score = 15  # cold but rideable
    elif 32 < temp_f <= 40:
        temp_score = 10  # getting slushy
    elif temp_f > 40:
        temp_score = -10  # slushy/icy risk
    else:
        temp_score = 5   # very cold

    # --- Wind penalty (high wind = bad time) ---
    if wind_speed_mph is None:
        wind_score = 0
    elif wind_speed_mph <= 10:
        wind_score = 15  # calm, great
    elif wind_speed_mph <= 20:
        wind_score = 0    # was 5, neutral not a bonus
    elif wind_speed_mph <= 35:
        wind_score = -15  # was -10, more punishing
    else:
        wind_score = -30  # was -25, likely lift closures

    # --- Conditions bonus ---
    if conditions is None:
        conditions_score = 0
    else:
        conditions_lower = conditions.lower()
        if "snow" in conditions_lower:
            conditions_score = 15  # fresh snow is great
        elif "clear" in conditions_lower or "sunny" in conditions_lower:
            conditions_score = 10  # bluebird day
        elif "cloud" in conditions_lower:
            conditions_score = 5   # overcast but fine
        elif "fog" in conditions_lower or "mist" in conditions_lower:
            conditions_score = -5  # low visibility
        elif "rain" in conditions_lower or "drizzle" in conditions_lower:
            conditions_score = -20  # worst case
        else:
            conditions_score = 0

    # --- Snowfall bonus ---
    if snowfall_in and snowfall_in > 0:
        snow_bonus = min(snowfall_in * 10, 15)  # cap at 15 pts
    else:
        snow_bonus = 0

    # --- Final score ---
    total = score + temp_score + wind_score + conditions_score + snow_bonus
    return max(0, min(100, total))  # clamp between 0-100


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

    # get latest reading per resort
    results = con.execute("""
        SELECT DISTINCT ON (resort)
            resort,
            state,
            temp_f,
            wind_speed_mph,
            snowfall_in,
            conditions,
            timestamp
        FROM conditions
        ORDER BY resort, fetched_at DESC
    """).fetchall()

    con.close()

    print("\n🏂 Ride Quality Scores\n")
    print(f"{'Resort':<20} {'Temp':>6} {'Wind':>8} {'Score':>7} {'Rating'}")
    print("-" * 65)

    for row in results:
        resort, state, temp_f, wind_mph, snowfall, conds, ts = row
        score = calculate_ride_score(temp_f, wind_mph, conds, snowfall)
        rating = grade(score)
        temp_str = f"{round(temp_f, 1)}°F"
        wind_str = f"{round(wind_mph, 1)}mph"
        print(f"{resort + ', ' + state:<20} {temp_str:>8} {wind_str:>10} {score:>7} {rating}")

if __name__ == "__main__":
    run()