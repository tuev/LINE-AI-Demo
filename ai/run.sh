#!/bin/bash

gunicorn -k uvicorn.workers.UvicornWorker \
    --bind :$PORT \
    --workers 1 \
    --threads 8 \
    --timeout 0 \
    --chdir src \
    main:app

