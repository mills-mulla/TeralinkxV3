#!/bin/bash
set -e

echo "🚀 Starting RADIUS API Application..."
echo "Database: ${DATABASE_URL:-postgresql://radius_user:password@db:5432/radius_db}"

# Extract database connection details from DATABASE_URL or use defaults
DB_HOST=${DB_HOST:-db}
DB_PORT=${DB_PORT:-5432}
RADIUS_DB_NAME=${RADIUS_POSTGRES_DB:-radius_db}
RADIUS_DB_USER=${RADIUS_POSTGRES_USER:-radius_user}

echo "Waiting for database at ${DB_HOST}:${DB_PORT}..."
while ! nc -z "$DB_HOST" "$DB_PORT"; do
  echo "  Database not ready, waiting..."
  sleep 2
done
echo "✅ Database is ready!"

echo "📝 Making migrations..."
python manage.py makemigrations --noinput

echo "🔄 Running migrations..."
python manage.py migrate --noinput

echo "📦 Collecting static files..."
python manage.py collectstatic --noinput --clear

# Initialize RADIUS data if needed
echo "🌱 Initializing RADIUS configuration..."
python manage.py shell << END
from django.conf import settings
import os

print(f'ℹ️  RADIUS Database: {os.getenv("RADIUS_POSTGRES_DB", "radius_db")}')
print(f'ℹ️  RADIUS User: {os.getenv("RADIUS_POSTGRES_USER", "radius_user")}')
print(f'✅ RADIUS API configuration initialized')
END

echo "🎉 RADIUS API initialization complete!"
echo "🌐 Starting RADIUS API server..."

exec "$@"
