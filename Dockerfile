FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy API requirements and install dependencies
COPY Fantasy-Football-API/requirements.txt /app/requirements.txt
RUN pip install --upgrade pip \
	&& pip install --no-cache-dir -r /app/requirements.txt

# Copy the API source code
COPY Fantasy-Football-API/ /app/

# Copy the data extraction folders
COPY ["Estrai listone/", "/data-root/Estrai listone/"]
COPY ["Estrai voti/", "/data-root/Estrai voti/"]

# Set environment variable for data directory
ENV BASE_DIR=/data-root

# Expose the port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
	CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/').read()"

# Run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]