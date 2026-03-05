import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import streamlit as st
import pandas as pd
import plotly.express as px
import anthropic
from dotenv import load_dotenv

load_dotenv()

from storage.db import get_connection
from scoring.scorer import calculate_ride_score, grade

st.set_page_config(
    page_title="🏂 NE Snow Conditions",
    page_icon="🏂",
    layout="wide"
)

st.title("🏂 New England Snow Conditions")
st.caption("Live ride quality scores powered by NOAA weather data")

tab1, tab2 = st.tabs(["Dashboard", "Ask the Snow Bot"])

# --- Load latest conditions per resort ---
@st.cache_data(ttl=300)
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
            rolling_72hr_snowfall,
            freeze_thaw_flag,
            fetched_at AS timestamp
        FROM features
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

# --- Tab 1: Dashboard ---
with tab1:
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

                if row.get("freeze_thaw_flag"):
                    st.warning("⚠️ Freeze/thaw detected — expect icy conditions today")

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

    fig = px.line(
        history,
        x="fetched_at",
        y="score",
        color="resort",
        markers=True,
        title="Ride Quality Score Over Time",
        labels={"fetched_at": "Time", "score": "Ride Score", "resort": "Resort"},
        range_y=[0, 100]
    )

    fig.update_traces(marker=dict(size=6))
    fig.update_layout(
        hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=-0.3),
        height=450
    )

    st.plotly_chart(fig, width='stretch')
    st.caption("Data refreshes every 5 minutes. Run the fetcher to update conditions.")

# --- Tab 2: Snow Bot ---
with tab2:
    st.subheader("Ask the Snow Bot")
    st.caption("Ask anything about current conditions across New England resorts")

    if "messages" not in st.session_state:
        st.session_state.messages = []

    # display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    def get_conditions_summary():
        con = get_connection()
        df = con.execute("""
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
        """).df()
        con.close()

        df["score"] = df.apply(
            lambda r: calculate_ride_score(
                r["temp_f"], r["wind_speed_mph"], r["conditions"],
                r["snowfall_in"], r["rolling_72hr_snowfall"], r["freeze_thaw_flag"]
            ), axis=1
        )
        df["rating"] = df["score"].apply(grade)

        summary = "Current New England ski resort conditions:\n\n"
        for _, row in df.iterrows():
            summary += f"{row['resort']}, {row['state']}:\n"
            summary += f"  - Temp: {round(row['temp_f'], 1)}F\n"
            summary += f"  - Wind: {round(row['wind_speed_mph'], 1)} mph\n"
            summary += f"  - Conditions: {row['conditions']}\n"
            summary += f"  - 72hr Snowfall: {round(row['rolling_72hr_snowfall'] or 0, 2)} inches\n"
            summary += f"  - Ice Risk: {'Yes' if row['freeze_thaw_flag'] else 'No'}\n"
            summary += f"  - Ride Score: {row['score']}/100 ({row['rating']})\n\n"
        return summary

    if prompt := st.chat_input("Ask about conditions, which resort to visit, best time to go..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Checking conditions..."):
                conditions = get_conditions_summary()
                client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

                response = client.messages.create(
                    model="claude-sonnet-4-20250514",
                    max_tokens=1000,
                    system=f"""You are a helpful snowboarding conditions assistant for New England resorts.
You have access to real-time conditions data and ride quality scores.
Be conversational, helpful, and specific. Give concrete recommendations.
Always reference actual current data in your responses.

Here is the current conditions data:
{conditions}""",
                    messages=[
                        {"role": m["role"], "content": m["content"]}
                        for m in st.session_state.messages
                    ]
                )

                reply = response.content[0].text
                st.markdown(reply)
                st.session_state.messages.append({"role": "assistant", "content": reply})