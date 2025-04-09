# Use a slim Python base
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Environment settings
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install system dependencies
RUN apt-get update && apt-get install -y gcc && apt-get clean

# Copy environment and install requirements
COPY .env .env
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && pip install -r requirements.txt

# Copy source
COPY . .

# Default command (can be overridden)
CMD ["python", "main.py"]
