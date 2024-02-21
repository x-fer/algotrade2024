#!/bin/bash
echo "Starting python virtual environment"
python -m venv .venv
python -m pip install --upgrade pip
nohup pip install -r requirements.txt > /dev/null 2>&1 &

echo "Running postgre server"
sudo service postgresql start

echo "Running migration script"
python run_migrations.py

if [[ "$TESTING" == 1 ]]; then
echo "Running main with reload"
TESTING=1 uvicorn main:app --reload
else
echo "Running uvicorn main with 4 workers"
TESTING=0 uvicorn main:app --workers 4
fi