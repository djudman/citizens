#!/bin/sh
docker build . -t citizens
mkdir -p logs
docker run -it --rm --name=citizens -v logs:/app/logs -p 8080:8080 citizens:latest
