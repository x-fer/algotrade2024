from databases import Database
from db.migration import run_migrations

DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/mydatabase"

database = Database(DATABASE_URL)


print("Database object created")
