#!/bin/sh
set -e

echo "Applying database migrations..."
uv run flask db upgrade

echo "Seeding demo data (idempotent, skips anything that already exists)..."
uv run flask seed-db

echo "Starting Flask dev server..."
exec uv run flask run --host=0.0.0.0 --debug
