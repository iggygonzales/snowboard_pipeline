import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from prefect import flow, task
from prefect.logging import get_run_logger
import subprocess

# ---Environment Detection---
# Detect whether we're running on EC2 or locally in VS Code
# This allows the same file to work in both environments without changes
IS_EC2 = os.path.exists("/home/ec2-user")

# Use the correct Python executable depending on environment
PYTHON = "/usr/bin/python3" if IS_EC2 else sys.executable

# Use the correct dbt executable depending on environment
# On EC2, dbt is installed in the ec2-user local bin
# Locally, dbt is available on the system PATH
DBT = "/home/ec2-user/.local/bin/dbt" if IS_EC2 else "dbt"

# Absolute path to the project root — used as working directory for subprocesses
PROJECT_ROOT = "/home/ec2-user/snowboard_pipeline" if IS_EC2 else os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

# Absolute path to the dbt project directory
DBT_DIR = os.path.join(PROJECT_ROOT, "transforms", "snow_transforms")


# ---Task 1: Fetch Conditions---
# retries=3 means Prefect will retry up to 3 times if NOAA API is down or flaky
# retry_delay_seconds=60 means wait 60 seconds between each retry
@task(retries=3, retry_delay_seconds=60)
def fetch_conditions():
    logger = get_run_logger()
    logger.info("Fetching conditions from NOAA...")
    
    # Run the fetcher as a subprocess so it uses the correct Python environment
    # capture_output=True captures stdout/stderr so we can log them
    result = subprocess.run(
        [PYTHON, "-m", "ingestion.noaa_fetcher"],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True
    )
    
    # If the fetcher exits with a non-zero code, raise an exception
    # This triggers Prefect's retry logic
    if result.returncode != 0:
        raise Exception(f"Fetcher failed: {result.stderr}")
    
    # Log the fetcher output to Prefect Cloud for visibility
    logger.info(result.stdout)
    return "conditions fetched"


# ---Task 2: Run dbt Transforms---
# retries=2 means Prefect will retry up to 2 times if dbt fails
# retry_delay_seconds=30 means wait 30 seconds between each retry
@task(retries=2, retry_delay_seconds=30)
def run_dbt():
    logger = get_run_logger()
    logger.info("Running dbt transforms...")
    
    # Run dbt as a subprocess from the dbt project directory
    result = subprocess.run(
        [DBT, "run"],
        cwd=DBT_DIR,
        capture_output=True,
        text=True
    )
    
    # If dbt exits with a non-zero code, raise an exception
    # This triggers Prefect's retry logic
    if result.returncode != 0:
        raise Exception(f"dbt failed: {result.stderr}")
    
    # Log the dbt output to Prefect Cloud for visibility
    logger.info(result.stdout)
    return "dbt complete"


# ---Flow Definition---
# The flow orchestrates both tasks in sequence:
# 1. Fetch conditions from NOAA and save to DuckDB
# 2. Run dbt transforms to rebuild feature tables
# wait_for=[conditions] ensures dbt only runs after the fetcher succeeds
@flow(name="snowboard-pipeline")
def snowboard_pipeline():
    conditions = fetch_conditions()
    dbt = run_dbt(wait_for=[conditions])
    return "pipeline complete"


# ---Entry Point---
# When run directly, start a long-running process that:
# - Listens for scheduled runs from Prefect Cloud
# - Runs the flow on the cron schedule (top of every hour)
# - Reports results back to Prefect Cloud
# On EC2, this is started with nohup so it runs in the background indefinitely
if __name__ == "__main__":
    snowboard_pipeline.serve(
        name="snowboard-hourly",    # deployment name visible in Prefect Cloud UI
        cron="0 * * * *"            # run at the top of every hour
    )