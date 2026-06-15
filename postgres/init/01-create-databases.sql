-- Creates the two application databases on first container startup.
--
-- This is a .sql file (not a .sh) on purpose: the postgres entrypoint runs *.sql
-- init files with `psql -f` (it only reads them), which avoids the exec /
-- permission / shebang pitfalls of bind-mounted shell scripts on macOS Docker.
-- The entrypoint runs this as POSTGRES_USER against POSTGRES_DB.

CREATE DATABASE arcade_db;
CREATE DATABASE auth_db;
