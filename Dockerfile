FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# System dependencies for Playwright/Chromium + XVFB (Virtual Display)
# Note: libgconf-2-4 removed as it is deprecated in newer Debian versions
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

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Install Python dependencies
RUN uv sync --frozen --no-dev --no-install-project
# Install SeleniumBase ChromeDriver
RUN /app/.venv/bin/seleniumbase install chromedriver
# Install Playwright Chromium
RUN /app/.venv/bin/playwright install chromium
# Copy project
COPY . .

# Use virtual environment
ENV PATH="/app/.venv/bin:$PATH"

# Collect static files
RUN python manage.py collectstatic --noinput

EXPOSE 8000

# xvfb-run : यह ग्यूनिकॉर्न को एक वर्चुअल डिस्प्ले के अंदर शुरू करेगा, ताकि क्रोम बिना एरर के खुल सके
CMD ["xvfb-run", "--server-args=-screen 0 1920x1080x24", "gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "1", "--timeout", "180"]
