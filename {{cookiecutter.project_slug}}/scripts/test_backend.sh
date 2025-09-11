#! /usr/bin/env bash

# Exit in case of error
set -e

docker-compose run --rm backend pytest $@