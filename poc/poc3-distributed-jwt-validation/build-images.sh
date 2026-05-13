#!/bin/bash
# Bouwt de Docker images voor POC 3.
# Vereist omdat 'docker stack deploy' de 'build:' directive negeert
# (zie Docker Swarm documentatie).

set -e

cd "$(dirname "$0")"

echo "Images bouwen..."

docker build -t hacklab/user-management:poc3      ./user-management
docker build -t hacklab/gateway:poc3              ./gateway
docker build -t hacklab/challenge-catalog:poc3    ./challenge-catalog
docker build -t hacklab/submission-validator:poc3 ./submission-validator

echo "Klaar. Deploy nu met:  docker stack deploy -f poc.yaml poc"
