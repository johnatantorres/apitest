#!/bin/sh

# Exit immediately if a command exits with a non-zero status.
set -e

# Run migrations
echo "Running database migrations..."
alembic upgrade head

# Seed data
echo "Seeding initial data..."
python seed_data.py

# Start server
echo "Starting FastAPI server..."
uvicorn app.main:app --host 0.0.0.0 --port 8000