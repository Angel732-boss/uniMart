#!/bin/bash
set -e

# Function to gracefully shut down uWSGI
shutdown_uwsgi() {
    echo "Received shutdown signal. Stopping uWSGI..."
    # Send SIGTERM to uWSGI master process
    kill -TERM "$uwsgi_pid" 2>/dev/null
    wait "$uwsgi_pid"
    echo "uWSGI stopped."
    exit 0
}

# Trap SIGTERM and SIGINT signals
trap 'shutdown_uwsgi' TERM INT

echo "Waiting for PostgreSQL (primary)..."
while ! nc -z postgres_primary 5432; do
  sleep 1
done
echo "PostgreSQL (primary) is up!"

echo "Waiting for PostgreSQL (replica)..."
while ! nc -z postgres_replica 5432; do
  sleep 1
done
echo "PostgreSQL (replica) is up!"

echo "Running database migrations on default (primary)..."
python manage.py migrate --database=default --noinput

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Starting uWSGI..."
exec uwsgi --ini /apps/uwsgi.ini &
uwsgi_pid=$!

set +e

wait "$uwsgi_pid"

# If wait exits (e.g., uWSGI crashes), log it
echo "uWSGI exited unexpectedly with code $?"
exit 1