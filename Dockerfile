FROM python:3.10-slim

WORKDIR /app/

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc libpq-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Cài đặt watchdog (để theo dõi thay đổi file tốt hơn)
RUN pip install watchdog

# Install Python dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt && \
    pip install pydantic-settings

# Copy project
COPY . /app/

# Make start script executable
RUN chmod +x /app/start.sh

# Use start.sh as entrypoint
COPY start.sh /app/
RUN chmod +x /app/start.sh