# ============================
# Stage 1: Builder
# ============================
FROM python:3.11-slim AS builder

WORKDIR /app

# Prevent .pyc & enable logs
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install build dependencies (removed later)
RUN apt-get update && apt-get install -y \
    gcc \
    build-essential \
    default-libmysqlclient-dev \
    netcat \
    && rm -rf /var/lib/apt/lists/*


# Install Python deps
COPY requirements.txt .
RUN pip install --upgrade pip \
    && pip install --prefix=/install -r requirements.txt


# ============================
# Stage 2: Final runtime image
# ============================
FROM python:3.11-slim

WORKDIR /app

# Create non-root user
RUN adduser --disabled-password --gecos '' appuser

# Copy installed packages from builder
COPY --from=builder /install /usr/local

# Copy app source code
COPY . .

# Set environment vars
ENV PATH="/usr/local/bin:$PATH"
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Expose FastAPI port
EXPOSE 8000

# Use non-root user
USER appuser

# Make entrypoint script executable
RUN chmod +x /app/entrypoint.sh

# Healthcheck (optional, good for K8s/Docker Swarm)
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
  CMD curl --fail http://localhost:8000/health || exit 1

# Entrypoint (runs Alembic + starts app)
ENTRYPOINT ["/app/entrypoint.sh"]
