#!/bin/bash

if [ ! -f "config.yml" ]; then
    echo "config.yml not found"
    exit 1
fi

bash ./install.sh

args=(-p 80 -H "0.0.0.0")

if [ -n "$RUN_ENV" ]; then
    [ "$RUN_ENV" = "development" ] && args+=(--development)
    [ "$RUN_ENV" = "production" ] && args+=(--production)
fi

if [ -n "$DEBUG" ]; then
    [[ ${DEBUG,,} == "true" || ${DEBUG,,} == "on" ]] && args+=(--debug)
fi

python3 ./web.py "${args[@]}"