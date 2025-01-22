#!/usr/bin/env bash

echo "Start service"

# migrate database
python scripts/migrate.py

exec uvicorn webapp.main:create_app --host=$BIND_IP --port=$BIND_PORT

docker network create -d bridge sirius_network