import duckdb
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "snowboard.duckdb")

def get_connection():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    return duckdb.connect(DB_PATH)

def initialize_db():
    con = get_connection()
    con.execute("""
        CREATE TABLE IF NOT EXISTS conditions (
            resort          VARCHAR,
            state           VARCHAR,
            timestamp       TIMESTAMP,
            temp_f          FLOAT,
            wind_speed_mph  FLOAT,
            snowfall_in     FLOAT,
            visibility_m    FLOAT,
            conditions      VARCHAR,
            fetched_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    con.execute("""
        CREATE TABLE IF NOT EXISTS forecasts (
            resort              VARCHAR,
            state               VARCHAR,
            period_name         VARCHAR,
            start_time          TIMESTAMP,
            end_time            TIMESTAMP,
            is_daytime          BOOLEAN,
            temp_f              FLOAT,
            wind_speed          VARCHAR,
            wind_direction      VARCHAR,
            short_forecast      VARCHAR,
            detailed_forecast   VARCHAR,
            fetched_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    con.close()
    print("Database initialized")

if __name__ == "__main__":
    initialize_db()