FROM python:3.11-slim

WORKDIR /app

# Install dbt dependencies
RUN apt-get update && apt-get install -y gcc && rm -rf /var/lib/apt/lists/*

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all project files
COPY config/ ./config/
COPY ingestion/ ./ingestion/
COPY storage/ ./storage/
COPY scoring/ ./scoring/
COPY dashboard/ ./dashboard/
COPY orchestration/ ./orchestration/
COPY transforms/ ./transforms/

# Create data and logs directories
RUN mkdir -p data logs

RUN mkdir -p /root/.dbt
COPY transforms/snow_transforms/profiles.yml /root/.dbt/profiles.yml

# Expose Streamlit port
EXPOSE 8501

# Run pipeline first, then start dashboard
CMD python -m ingestion.noaa_fetcher && \
    cd transforms/snow_transforms && dbt run && cd /app && \
    (while true; do sleep 3600 && python -m ingestion.noaa_fetcher && cd transforms/snow_transforms && dbt run && cd /app; done) & \
    streamlit run dashboard/app.py --server.port=8501 --server.address=0.0.0.0
