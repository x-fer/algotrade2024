#!/bin/bash
# echo "Starting python virtual environment"
# python -m venv .venv
# python -m pip install --upgrade pip
# nohup pip install -r requirements.txt > /dev/null 2>&1 &

echo "TODO Running redis server"

echo "Running migration script"
python run_migrations.py

echo "Running redis server"
redis-server --daemonize yes

if [[ "$TESTING" == 1 ]]; then
echo "Running main with reload"
DROP_TABLES=1 FILL_DATASETS=1 FILL_GAMES=1 WATCHFILES_FORCE_POLLING=1 uvicorn main:app --reload --host=0.0.0.0 --port=3000
else
echo "Running uvicorn main with 4 workers"
TESTING=0 uvicorn main:app --workers 4 --host=0.0.0.0 --port=3000
fi