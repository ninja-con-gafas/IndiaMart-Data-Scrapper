#!/bin/bash

set -euo pipefail

ENV_FILE=".env"
DEFAULTS_SET=false

echo "Checking for .env file"

# Load existing environment variables if .env exists, else create .env
if [[ -f "$ENV_FILE" ]]; then
    echo ".env file found. Loading environment variables."
    set -o allexport
    source "$ENV_FILE"
    set +o allexport
else
    echo ".env file not found. Creating one with default values."
    touch "$ENV_FILE"
    DEFAULTS_SET=true
fi

# Function to set a default env var if not already set
# Args: $1 = var name, $2 = default value
function set_default() {
    local VAR_NAME="$1"
    local DEFAULT_VALUE="$2"
    # Check if var is empty or unset in current environment
    if [[ -z "${!VAR_NAME:-}" ]]; then
        echo "$VAR_NAME=$DEFAULT_VALUE" >> "$ENV_FILE"
        echo "$VAR_NAME not set, using default: $DEFAULT_VALUE"
        DEFAULTS_SET=true
    fi
}

set_default "AIRFLOW_ADMIN_EMAIL" "admin@example.com"
set_default "AIRFLOW_ADMIN_FIRST_NAME" "Administrator"
set_default "AIRFLOW_ADMIN_LAST_NAME" "System"
set_default "AIRFLOW_ADMIN_PASSWORD" "admin"
set_default "AIRFLOW_ADMIN_USERNAME" "admin"
set_default "AIRFLOW_WEBSERVER_SECRET_KEY" "airflowsecretkey"

set_default "DATA" "./data"

set_default "POSTGRES_AIRFLOW_DATABASE" "airflow"
set_default "POSTGRES_AIRFLOW_PASSWORD" "airflowpassword"
set_default "POSTGRES_AIRFLOW_USERNAME" "airflow"
set_default "POSTGRES_USERNAME" "postgres"
set_default "POSTGRES_PASSWORD" "postgrespassword"
set_default "POSTGRES_PRODUCTS_DATABASE" "products"
set_default "POSTGRES_PRODUCTS_PASSWORD" "productsdatabasepassword"
set_default "POSTGRES_PRODUCTS_USERNAME" "slooze"

set_default "AIRFLOW__CELERY__RESULT_BACKEND" "db+postgresql://airflow:airflowpassword@postgres/airflow"
set_default "AIRFLOW_CONN_PRODUCTS_DB" "postgresql+psycopg2://products:productsdatabasepassword@postgres/slooze"
set_default "AIRFLOW__DATABASE__SQL_ALCHEMY_CONN" "postgresql+psycopg2://airflow:airflowpassword@postgres/airflow"

set -o allexport
source "$ENV_FILE"
set +o allexport

if [[ "$DEFAULTS_SET" = true ]]; then
    echo "Defaults applied. You can edit the .env file to customize settings."
else
    echo "All required environment variables are already set."
fi

echo "Ensuring data directory exists at '$DATA' with correct permissions"
mkdir -p "$DATA"
sudo chmod u+rwx,g+rwx,o+rwx "$DATA"

echo "Creating init.sql for PostgreSQL"
mkdir -p ./infrastructure/postgres
cat > ./infrastructure/postgres/init.sql <<EOF
-- Create databases
CREATE DATABASE ${POSTGRES_AIRFLOW_DATABASE};
CREATE DATABASE ${POSTGRES_PRODUCTS_DATABASE};

-- Create users and grant privileges
CREATE USER ${POSTGRES_AIRFLOW_USERNAME} WITH PASSWORD '${POSTGRES_AIRFLOW_PASSWORD}';
GRANT ALL PRIVILEGES ON DATABASE ${POSTGRES_AIRFLOW_DATABASE} TO ${POSTGRES_AIRFLOW_USERNAME};

CREATE USER ${POSTGRES_PRODUCTS_USERNAME} WITH PASSWORD '${POSTGRES_PRODUCTS_PASSWORD}';
GRANT ALL PRIVILEGES ON DATABASE ${POSTGRES_PRODUCTS_DATABASE} TO ${POSTGRES_PRODUCTS_USERNAME};

-- Ensure permissions on future tables and schemas
ALTER DATABASE ${POSTGRES_AIRFLOW_DATABASE} OWNER TO ${POSTGRES_AIRFLOW_USERNAME};
ALTER DATABASE ${POSTGRES_PRODUCTS_DATABASE} OWNER TO ${POSTGRES_PRODUCTS_USERNAME};

-- Grant privileges on schemas
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO ${POSTGRES_AIRFLOW_USERNAME};
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO ${POSTGRES_PRODUCTS_USERNAME};
EOF

echo "Building the project with docker-compose"
docker compose -f ./docker-compose.yml build

echo "Application successfully built!"
echo "Run \`docker compose up -d\` to deploy the application."
