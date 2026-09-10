#!/bin/bash
# 1. डेटाबेस माइग्रेशन चलाएं
python manage.py migrate --noinput

# 2. Xvfb (वर्चुअल स्क्रीन) को बैकग्राउंड में शुरू करें
Xvfb :99 -screen 0 1920x1080x24 &
export DISPLAY=:99

# 3. Gunicorn को Render के डायनामिक $PORT पर शुरू करें
echo "Starting Gunicorn on port $PORT..."
gunicorn config.wsgi:application --bind 0.0.0.0:$PORT --workers 1 --timeout 180
