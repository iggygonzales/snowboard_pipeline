import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import streamlit as st
import pandas as pd
from storage.db import get_connection
from scoring.scorer import calculate_ride_score, grade

st.set_page_config(
    page_title="🏂 NE Snow Conditions",
    page_icon="🏂",
    layout="wide"
)

st.title("🏂 New England Snow Conditions")
st.caption("Live ride quality scores powered by NOAA weather data")

# --- Load latest conditions per resort ---
@st.cache_data(ttl=300)  # refresh every 5 minutes
def load_conditions():
    con = get_connection()
    df = con.execute("""
        SELECT DISTINCT ON (resort)
            resort,
            state,
            temp_f,
            wind_speed_mph,
            snowfall_in,
            conditions,
            timestamp,
            fetched_at
        FROM conditions
        ORDER BY resort, fetched_at DESC
    """).df()
    con.close()
    return df

df = load_conditions()

if df.empty:
    st.warning("No data yet — run the fetcher first.")
    st.stop()

# --- Add scores ---
df["score"] = df.apply(
    lambda r: calculate_ride_score(
        r["temp_f"], r["wind_speed_mph"], r["conditions"], r["snowfall_in"]
    ), axis=1
)
df["rating"] = df["score"].apply(grade)
df = df.sort_values("score", ascending=False)

# --- Summary metric row ---
st.subheader("Today's Leaderboard")
cols = st.columns(len(df))

for i, (_, row) in enumerate(df.iterrows()):
    with cols[i]:
        st.metric(
            label=f"{row['resort']}, {row['state']}",
            value=f"{row['score']}/100",
            delta=None
        )
        st.caption(row["rating"])

st.divider()

# --- Detail cards ---
st.subheader("Resort Details")
col1, col2 = st.columns(2)

for i, (_, row) in enumerate(df.iterrows()):
    col = col1 if i % 2 == 0 else col2
    with col:
        with st.container(border=True):
            st.markdown(f"### {row['rating']} — {row['resort']}, {row['state']}")
            m1, m2, m3 = st.columns(3)
            m1.metric("Temperature", f"{round(row['temp_f'], 1)}°F")
            m2.metric("Wind", f"{round(row['wind_speed_mph'], 1)} mph")
            m3.metric("Score", f"{row['score']}/100")
            st.caption(f"🌤 {row['conditions']}")
            st.caption(f"Last updated: {row['timestamp']}")

st.divider()

# --- Historical chart ---
st.subheader("Score History")

@st.cache_data(ttl=300)
def load_history():
    con = get_connection()
    df = con.execute("""
        SELECT
            resort,
            fetched_at,
            temp_f,
            wind_speed_mph,
            snowfall_in,
            conditions
        FROM conditions
        ORDER BY fetched_at ASC
    """).df()
    con.close()
    return df

history = load_history()
history["score"] = history.apply(
    lambda r: calculate_ride_score(
        r["temp_f"], r["wind_speed_mph"], r["conditions"], r["snowfall_in"]
    ), axis=1
)

chart_data = history.pivot_table(
    index="fetched_at",
    columns="resort",
    values="score"
)

st.line_chart(chart_data)

st.caption("Data refreshes every 5 minutes. Run the fetcher to update conditions.")
