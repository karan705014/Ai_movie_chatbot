FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# System dependencies for Playwright/Chromium + XVFB
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
    dos2unix \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Install Python dependencies
RUN uv sync --frozen --no-dev --no-install-project

# Install SeleniumBase ChromeDriver and Playwright Chromium
RUN /app/.venv/bin/seleniumbase install chromedriver
RUN /app/.venv/bin/playwright install chromium

# Copy project files
COPY . .

# Use virtual environment
ENV PATH="/app/.venv/bin:$PATH"

# Collect static files
RUN python manage.py collectstatic --noinput

# Render के पोर्ट को सपोर्ट करने के लिए
ENV PORT=10000
EXPOSE ${PORT}

# विंडोज की वजह से आने वाले लाइन फॉर्मेट एरर को ठीक करने के लिए dos2unix चलाएं
RUN dos2unix /app/start.sh && chmod +x /app/start.sh

# कंटेनर शुरू होने पर स्टार्ट स्क्रिप्ट को चलाएं
CMD ["/app/start.sh"]