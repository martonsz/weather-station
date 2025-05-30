#!/bin/sh
docker compose -f compose.yml -f compose.traefik.yml --env-file marton.cloud.env up -d
