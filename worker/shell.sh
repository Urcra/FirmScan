#!/bin/sh

docker build . -t worker
docker run -it worker /bin/bash
