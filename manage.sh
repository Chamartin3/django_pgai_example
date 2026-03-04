#!/bin/bash
# Proxy script to run Django management commands in Docker
#
# Uses the running 'django' service if available (fast: no uv sync overhead),
# otherwise falls back to 'docker compose run --rm' (slow but always works).

set -e

# Escape arguments for safe passing through bash -c
escaped_args=""
for arg in "$@"; do
    escaped_args+="$(printf '%q ' "$arg")"
done

# Check if the django service container is running
if docker compose ps --status running django 2>/dev/null | grep -q "django"; then
    docker compose exec django bash -c "uv run python manage.py $escaped_args"
else
    docker compose run --rm django bash -c "uv sync && uv run python manage.py $escaped_args"
fi
