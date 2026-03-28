#!/bin/bash
set -e

echo "🚀 Starting TeralinkX Django Application..."
echo "Database: ${DATABASE_URL:-postgresql://teralinkx:password@db:5432/teralinkx}"
echo "Debug Mode: ${DEBUG:-False}"

# Extract database connection details from DATABASE_URL or use defaults
DB_HOST=${DB_HOST:-db}
DB_PORT=${DB_PORT:-5432}
DB_NAME=${POSTGRES_DB:-teralinkx}
DB_USER=${POSTGRES_USER:-teralinkx}

echo "Waiting for database at ${DB_HOST}:${DB_PORT}..."
while ! nc -z "$DB_HOST" "$DB_PORT"; do
  echo "  Database not ready, waiting..."
  sleep 2
done
echo "✅ Database is ready!"

# Test database connection
echo "Testing database connection..."
python manage.py check_db_connections || {
  echo "❌ Database connection failed"
  exit 1
}

echo "📝 Making migrations..."
python manage.py makemigrations --noinput

echo "🔄 Running migrations..."
python manage.py migrate --noinput

echo "📦 Collecting static files..."
python manage.py collectstatic --noinput --clear

echo "🌱 Populating initial data..."
python manage.py populate_data

echo "👤 Creating superuser if not exists..."
python manage.py shell << END
from django.contrib.auth import get_user_model
import os

User = get_user_model()

# Get credentials from environment variables
username = os.getenv('DJANGO_SUPERUSER_USERNAME', 'admin')
email = os.getenv('DJANGO_SUPERUSER_EMAIL', 'admin@teralinkx.com')
password = os.getenv('DJANGO_SUPERUSER_PASSWORD', 'admin')

if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(username, email, password)
    print(f'✅ Superuser "{username}" created successfully')
else:
    print(f'ℹ️  Superuser "{username}" already exists')
END

echo "🎉 Django application initialization complete!"
echo "🌐 Starting application server..."

exec "$@"
