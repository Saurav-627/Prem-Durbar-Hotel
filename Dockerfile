# Use official Python slim bookworm image
FROM python:3.12-slim-bookworm

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/app/.venv/bin:$PATH"

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy UV installer from the official image
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Install dependencies using UV (without syncing code yet)
RUN uv sync --frozen --no-install-project

# Copy project files
COPY . .

# Install the project itself (if needed)
RUN uv sync --frozen

# Expose port
EXPOSE 8000

# Run entrypoint script
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000"]
