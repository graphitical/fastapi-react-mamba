#! /usr/bin/env bash

# Exit in case of error
set -e

# Run this from the root of the project
cookiecutter --no-input -f ./ project_slug="testing-project"

cd testing-project

docker-compose build
docker-compose down -v --remove-orphans
docker-compose up -d
# Run migrations first
docker-compose run --rm backend alembic upgrade head

# Backend/frontend tests
./scripts/test.sh

# Cleanup
docker-compose down -v --remove-orphans

# only remove directory if running locally
if [[ -z "$CIRCLE_CI_ENV" ]]; then
    echo "Cleaning up generated project locally..."
    cd ..
    # Try local removal first; if it fails (e.g., due to root-owned files from Docker), fallback to containerized cleanup.
    if rm -rf testing-project 2>/dev/null; then
        echo "Removed testing-project"
    else
        echo "Local removal failed; retrying with Docker as root..."
        # Mount the parent directory and remove the folder from within a root container to avoid sudo.
        docker run --rm -v "$PWD":/host busybox sh -c 'rm -rf /host/testing-project' || true
        if [[ -d testing-project ]]; then
            echo "Warning: testing-project still exists. You may need to run: sudo rm -rf testing-project"
        else
            echo "Removed testing-project via Docker"
        fi
    fi
fi
