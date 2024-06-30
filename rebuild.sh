#!/bin/sh

docker rm -f hooks
docker image rm hooks
docker build --env-file .env -t hooks .
docker run --name hooks --restart=always -p 9001:9000 -d hooks -verbose -hooks=/etc/webhook/hooks.json -hotreload
