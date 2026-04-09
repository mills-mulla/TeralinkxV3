#!/bin/bash
set -e

echo "🔧 Running database migrations..."
python manage.py migrate --noinput

echo "✅ Migrations complete!"
echo "🚀 Starting Gunicorn..."
exec gunicorn teralinkx.wsgi:application --bind 0.0.0.0:8000 --workers 4 --timeout 120
