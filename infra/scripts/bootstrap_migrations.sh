#!/usr/bin/env bash
# Run Alembic migrations (bootstrap). Use after Postgres is up.
# Usage: DATABASE_URL=postgresql://... ./infra/scripts/bootstrap_migrations.sh

set -e
cd "$(dirname "$0")/../../backend"
export PYTHONPATH=.
export DATABASE_URL="${DATABASE_URL:-postgresql://aluminum:aluminum@localhost:5432/aluminum}"
alembic upgrade head
echo "Migrations complete."
