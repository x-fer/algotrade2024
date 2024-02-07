## How to run

    sudo service postgresql start
    TESTING=1 uvicorn main:app --reload

## Run tests

    pytest -s .
    pip install pytest-asyncio  

## How to setup postgre

Valjda ovo radi:

    pip install asyncpg
    
    apt install postgresql postgresql-contrib
    sudo service postgresql start
    sudo -u postgres psql
    sudo -u postgres psql -c "ALTER ROLE postgres WITH password 'postgres'"
    sudo -u postgres psql -c "CREATE DATABASE mydatabase"
    sudo -u postgres psql -c "CREATE DATABASE test_database"
    