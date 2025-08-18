# ============================
# Stage 1: Base Image
# ============================
FROM python:3.11-slim AS base

# Set working directory
WORKDIR /app

# Prevent Python from writing .pyc files & enable logs
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install system dependencies (needed for MySQL client + Alembic)
RUN apt-get update && apt-get install -y \
    gcc \
    default-libmysqlclient-dev \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# ============================
# Stage 2: Install dependencies
# ============================
FROM base AS builder

COPY requirements.txt .
RUN pip install --upgrade pip \
    && pip install -r requirements.txt

# ============================
# Stage 3: Final image
# ============================
FROM base

COPY --from=builder /usr/local /usr/local

# Copy project files
COPY . .

# Expose FastAPI default port
EXPOSE 8000

# Entrypoint script (to handle migrations + app start)
RUN chmod +x /app/entrypoint.sh

ENTRYPOINT ["/app/entrypoint.sh"]
