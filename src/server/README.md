## How to run

    > sudo service postgresql start

    > uvicorn server:app --reload

## Run tests

    > pytest .

    > pip install pytest-asyncio  

## How to setup postgre

Valjda ovo radi:

    pip install asyncpg
    
    apt install postgresql postgresql-contrib
    sudo -u postgres psql
    sudo -u postgres psql -c "ALTER ROLE postgres WITH password 'postgres'"
    sudo -u postgres psql -c "CREATE DATABASE mydatabase"
    