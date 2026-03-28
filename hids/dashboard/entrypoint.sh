#!/bin/bash
set -e

echo "🚀 Starting HIDS Dashboard..."
echo "Database: ${POSTGRES_HOST:-db}:${POSTGRES_PORT:-5432}/${POSTGRES_DB:-hids}"

# Extract database connection details
DB_HOST=${POSTGRES_HOST:-db}
DB_PORT=${POSTGRES_PORT:-5432}
DB_NAME=${POSTGRES_DB:-hids}
DB_USER=${POSTGRES_USER:-hids}

# Wait for database
echo "Waiting for database at ${DB_HOST}:${DB_PORT}..."
while ! nc -z "$DB_HOST" "$DB_PORT"; do
  echo "  Database not ready, waiting..."
  sleep 2
done
echo "✅ Database is ready!"

# Wait for HIDS engine
echo "Waiting for HIDS engine..."
attempt=1
max_attempts=30
while ! nc -z hids_engine 5003 2>/dev/null; do
  if [[ $attempt -ge $max_attempts ]]; then
    echo "⚠️  HIDS engine not available after ${max_attempts} attempts"
    echo "   Dashboard will start but some features may not work"
    break
  fi
  echo "  HIDS engine not ready, waiting... (attempt $attempt/$max_attempts)"
  sleep 2
  ((attempt++))
done

if nc -z hids_engine 5003 2>/dev/null; then
  echo "✅ HIDS engine is ready!"
fi

# Wait for ML service
echo "Waiting for ML service..."
attempt=1
while ! nc -z hids_ml_service 5001 2>/dev/null; do
  if [[ $attempt -ge $max_attempts ]]; then
    echo "⚠️  ML service not available after ${max_attempts} attempts"
    echo "   Dashboard will start but ML features may not work"
    break
  fi
  echo "  ML service not ready, waiting... (attempt $attempt/$max_attempts)"
  sleep 2
  ((attempt++))
done

if nc -z hids_ml_service 5001 2>/dev/null; then
  echo "✅ ML service is ready!"
fi

# Test database connection
echo "Testing database connection..."
python3 << END
import psycopg2
import os
import sys

try:
    conn = psycopg2.connect(
        host=os.getenv('POSTGRES_HOST', 'db'),
        port=os.getenv('POSTGRES_PORT', '5432'),
        database=os.getenv('POSTGRES_DB', 'hids'),
        user=os.getenv('POSTGRES_USER', 'hids'),
        password=os.getenv('POSTGRES_PASSWORD', 'hidspass')
    )
    conn.close()
    print('✅ Database connection successful!')
except Exception as e:
    print(f'❌ Database connection failed: {e}')
    sys.exit(1)
END

echo "🎉 HIDS Dashboard initialization complete!"
echo "🌐 Starting dashboard server on port ${DASHBOARD_PORT:-5002}..."

exec "$@"
