#!/bin/bash

# docker swarm gaat zelf geen images builden dus we moeten dat zelf doen

docker build -t poc4-producer:latest ./producer
docker build -t poc4-consumer:latest ./consumer

# stack deployen
docker stack deploy -c poc.yml poc4

