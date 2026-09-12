FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install uv (Astral fast installer)
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Complete Linux GUI Dependencies for Playwright & SeleniumBase Web Drivers
RUN apt-get update && apt-get install -y \
    curl \
    wget \
    ca-certificates \
    chromium \
    libnss3 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libasound2 \
    libpangocairo-1.0-0 \
    libpango-1.0-0 \
    libcairo2 \
    libatspi2.0-0 \
    libgtk-3-0 \
    fonts-liberation \
    xvfb \
    libxi6 \
    x11-utils \
    scrot \
    python3-tk \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency definition files
COPY pyproject.toml uv.lock ./

# Sync Python environment
RUN uv sync --frozen --no-dev --no-install-project

# Force install and download standalone web driver binaries inside virtual env
RUN /app/.venv/bin/seleniumbase install chromedriver
RUN /app/.venv/bin/playwright install chromium
# CRITICAL: Download system-level headless browser dependencies for Playwright
RUN /app/.venv/bin/playwright install-deps

# Copy rest of the project
COPY . .

# Set environment paths
ENV PATH="/app/.venv/bin:$PATH"

# Trigger Django staticfiles generation
RUN python manage.py collectstatic --noinput

# Bind Dynamic Port Configuration for Railway Engine mapping
ENV PORT=10000
EXPOSE ${PORT}

# Safely boots Xvfb virtual frame display and routes async requests via multi-threaded workers
CMD ["bash", "-c", "rm -f /tmp/.X99-lock && Xvfb :99 -screen 0 1920x1080x24 & export DISPLAY=:99 && python manage.py migrate --noinput && gunicorn config.wsgi:application --bind 0.0.0.0:$PORT --workers 1 --worker-class gthread --threads 2 --timeout 180"]
