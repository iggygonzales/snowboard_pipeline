import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from prefect import flow, task
from prefect.logging import get_run_logger
import subprocess

# detect if running on EC2 or locally
IS_EC2 = os.path.exists("/home/ec2-user")

PYTHON = "/usr/bin/python3" if IS_EC2 else sys.executable
DBT = "/home/ec2-user/.local/bin/dbt" if IS_EC2 else "dbt"
PROJECT_ROOT = "/home/ec2-user/snowboard_pipeline" if IS_EC2 else os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DBT_DIR = os.path.join(PROJECT_ROOT, "transforms", "snow_transforms")

@task(retries=3, retry_delay_seconds=60)
def fetch_conditions():
    logger = get_run_logger()
    logger.info("Fetching conditions from NOAA...")
    
    result = subprocess.run(
        [PYTHON, "-m", "ingestion.noaa_fetcher"],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        raise Exception(f"Fetcher failed: {result.stderr}")
    
    logger.info(result.stdout)
    return "conditions fetched"

@task(retries=2, retry_delay_seconds=30)
def run_dbt():
    logger = get_run_logger()
    logger.info("Running dbt transforms...")
    
    result = subprocess.run(
        [DBT, "run"],
        cwd=DBT_DIR,
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        raise Exception(f"dbt failed: {result.stderr}")
    
    logger.info(result.stdout)
    return "dbt complete"

@flow(name="snowboard-pipeline")
def snowboard_pipeline():
    conditions = fetch_conditions()
    dbt = run_dbt(wait_for=[conditions])
    return "pipeline complete"

if __name__ == "__main__":
    snowboard_pipeline()