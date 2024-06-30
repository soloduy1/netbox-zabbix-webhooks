#!/bin/sh

docker run --name hooks --restart=always -p 9001:9000 -d hooks -verbose -hooks=/etc/webhook/hooks.json -hotreload
