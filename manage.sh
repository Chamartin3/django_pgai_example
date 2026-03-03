#!/bin/bash
# Proxy script to run Django management commands in Docker

set -e

# Escape arguments for safe passing to docker compose
escaped_args=""
for arg in "$@"; do
    escaped_args+="$(printf '%q ' "$arg")"
done

# Run Django command in container with uv
docker compose run --rm django bash -c "uv sync > /dev/null 2>&1 && uv run python manage.py $escaped_args"
