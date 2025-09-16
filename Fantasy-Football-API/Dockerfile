FROM python:3.11-slim

# App directory
WORKDIR /app

# Copy requirements and install
COPY requirements.txt /app/requirements.txt
RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r /app/requirements.txt

# Copy only the API code (build context should be the folder containing this Dockerfile)
COPY . /app

# By default expect data to be mounted at /data. Override BASE_DIR if you bake data into the image.
ENV BASE_DIR=/data

EXPOSE 8000

# Run with 2 workers for a small production workload
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
