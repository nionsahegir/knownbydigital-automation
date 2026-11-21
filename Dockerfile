# Production Dockerfile for Known By Digital Social Automation
FROM mcr.microsoft.com/playwright/python:v1.49.0-noble

# Prevent Python from writing .pyc files and enable unbuffered logging
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV TZ=Asia/Dhaka

# Install ffmpeg and fonts
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    fonts-inter \
    fonts-liberation \
    tzdata \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright browser
RUN playwright install chromium

# Copy application files
COPY . .

# Run the 24/7 autonomous scheduler daemon
CMD ["python", "scheduler_daemon.py"]
