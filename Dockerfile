FROM python:3.11-slim

WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY config/ ./config/
COPY ingestion/ ./ingestion/
COPY storage/ ./storage/
COPY scoring/ ./scoring/
COPY dashboard/ ./dashboard/

# Create data and logs directories
RUN mkdir -p data logs

# Expose Streamlit port
EXPOSE 8501

# Run the dashboard by default
CMD ["streamlit", "run", "dashboard/app.py", "--server.port=8501", "--server.address=0.0.0.0"]