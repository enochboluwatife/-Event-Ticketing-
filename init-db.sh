#!/bin/bash
set -e

echo "Initializing databases: $POSTGRES_MULTIPLE_DATABASES"

# Function to check if database exists
database_exists() {
    local db="$1"
    local query="SELECT 1 FROM pg_database WHERE datname = '$db';"
    local result=$(psql -U "$POSTGRES_USER" -tAc "$query")
    [ "$result" = "1" ]
}

# Function to check if PostGIS extension exists in database
postgis_extension_exists() {
    local db="$1"
    local query="SELECT 1 FROM pg_extension WHERE extname = 'postgis';"
    local result=$(psql -U "$POSTGRES_USER" -d "$db" -tAc "$query" 2>/dev/null || echo "0")
    [ "$result" = "1" ]
}

# Process each database
for db in $(echo $POSTGRES_MULTIPLE_DATABASES | tr ',' ' '); do
    if ! database_exists "$db"; then
        echo "Creating database: $db"
        createdb -U "$POSTGRES_USER" "$db"
    fi

    echo "Ensuring PostGIS extension in database: $db"
    if ! postgis_extension_exists "$db"; then
        echo "Adding PostGIS extension to $db"
        psql -v ON_ERROR_STOP=1 -U "$POSTGRES_USER" -d "$db" <<-EOSQL
            CREATE EXTENSION IF NOT EXISTS postgis;
EOSQL
    fi
done

echo "Database initialization complete"
