#!/bin/bash
# Creates the two application databases on first container startup.
set -e

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    CREATE DATABASE arcade_db;
    CREATE DATABASE auth_db;
EOSQL
