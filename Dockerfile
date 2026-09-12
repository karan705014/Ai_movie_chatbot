FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install uv (Astral lightning-fast package installer)
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Complete Linux GUI Dependencies for virtual screen display handling
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

# Copy python configuration blueprints
COPY pyproject.toml uv.lock ./

# Synchronize virtual env packages securely
RUN uv sync --frozen --no-dev --no-install-project

# Download stable web binaries into the local virtual environment layer
RUN /app/.venv/bin/seleniumbase install chromedriver
RUN /app/.venv/bin/playwright install chromium

# Copy the rest of the application codebase
COPY . .

# Inject environment routing parameters
ENV PATH="/app/.venv/bin:$PATH"

# Run collectstatic to bind server asset parameters
RUN python manage.py collectstatic --noinput

# Render Dynamic Port configuration layout
ENV PORT=10000
EXPOSE ${PORT}

# Clean old virtual frame display locks, boot display :99, and launch multi-threaded gthread workers
CMD ["bash", "-c", "rm -f /tmp/.X99-lock && Xvfb :99 -screen 0 1920x1080x24 & export DISPLAY=:99 && python manage.py migrate --noinput && gunicorn config.wsgi:application --bind 0.0.0.0:$PORT --workers 1 --worker-class gthread --threads 2 --timeout 180"]
