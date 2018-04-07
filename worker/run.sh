#!/bin/sh

docker build . -t worker
docker run --net="host" worker
