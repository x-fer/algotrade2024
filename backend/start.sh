#!/bin/bash
echo "Starting python virtual environment"
# python -m venv .venv
# python -m pip install --upgrade pip
# nohup pip install -r requirements.txt > /dev/null 2>&1 &

echo "TODO Running redis server"


if [[ "$TESTING" == 1 ]]; then
    export DROP_TABLES=1 FILL_DATASETS=1 FILL_TABLES=1
fi

echo "Running migration script"
python run_migrations.py

# echo "Running redis server"
# redis-server --daemonize yes

if [[ "$TESTING" == 1 ]]; then
    echo "Running main with reload"
    export WATCHFILES_FORCE_POLLING=1
    uvicorn main:app --reload --host=0.0.0.0 --port=3000 --log-level critical
else
    echo "Running uvicorn main with 4 workers"
    uvicorn main:app --workers 4 --host=0.0.0.0 --port=3000 --log-level warning
fi