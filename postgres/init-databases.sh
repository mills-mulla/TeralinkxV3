#!/bin/bash
set -e

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    SELECT 'CREATE DATABASE hids'
    WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'hids')\gexec

    DO \$\$
    BEGIN
        IF NOT EXISTS (SELECT FROM pg_user WHERE usename = 'hids') THEN
            CREATE USER hids WITH PASSWORD 'hidspass';
        END IF;
    END
    \$\$;

    GRANT ALL PRIVILEGES ON DATABASE hids TO hids;

    SELECT 'CREATE DATABASE radius'
    WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'radius')\gexec

    DO \$\$
    BEGIN
        IF NOT EXISTS (SELECT FROM pg_user WHERE usename = 'radius') THEN
            CREATE USER radius WITH PASSWORD 'radiuspass';
        END IF;
    END
    \$\$;

    GRANT ALL PRIVILEGES ON DATABASE radius TO radius;
EOSQL
