# =============================================================================
# Insurance Claims Processing System - Multi-stage Dockerfile
# =============================================================================

FROM python:3.9-slim as base

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    unzip \
    libaio1 \
    && rm -rf /var/lib/apt/lists/*

# Install Oracle Instant Client
RUN curl -o /tmp/instantclient.zip https://download.oracle.com/otn_software/linux/instantclient/2340000/instantclient-basic-linux.x64-23.4.0.24.05.zip \
    && unzip /tmp/instantclient.zip -d /opt/oracle \
    && rm /tmp/instantclient.zip \
    && echo /opt/oracle/instantclient_23_4 > /etc/ld.so.conf.d/oracle-instantclient.conf \
    && ldconfig

ENV LD_LIBRARY_PATH=/opt/oracle/instantclient_23_4:$LD_LIBRARY_PATH

WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# =============================================================================
# API Image
# =============================================================================
FROM base as api

EXPOSE 8000

CMD ["python", "run_api.py"]

# =============================================================================
# UI Image
# =============================================================================
FROM base as ui

EXPOSE 8501

CMD ["python", "run_ui.py"]
