#!/usr/bin/env bash
set -euo pipefail


ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT_DIR"

echo "Starting docker compose (build + up)"
docker compose up -d --build

echo "Waiting for web container readiness (attempts: 30)..."
max_attempts=30
attempt=0
until docker compose exec web python -c "import sys; sys.exit(0)" >/dev/null 2>&1; do
  attempt=$((attempt+1))
  if [ "$attempt" -ge "$max_attempts" ]; then
    echo "Reached max attempts ($max_attempts). Proceeding to migration anyway."
    break
  fi
  echo "Attempt $attempt/$max_attempts — sleeping 2s"
  sleep 2
done

echo "Running migrations inside web container..."
if docker compose exec web python -m app.migrate; then
  echo "Migration succeeded."
else
  echo "Exec migration failed — trying run --rm"
  docker compose run --rm web python -m app.migrate
fi

echo "Running seed inside web container..."
if docker compose exec web python -m app.seed; then
  echo "Seed succeeded."
else
  echo "Exec seed failed — trying run --rm"
  docker compose run --rm web python -m app.seed
fi

echo "Done."
