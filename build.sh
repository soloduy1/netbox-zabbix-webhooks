#!/bin/bash

docker build --env-file .env -t hooks .
