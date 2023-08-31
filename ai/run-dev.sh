#!/bin/bash

cd /app/src
uvicorn --host 0.0.0.0 --port $PORT main:app --reload
cd -
