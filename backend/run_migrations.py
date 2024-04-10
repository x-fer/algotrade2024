from db import migration, database
from config import config
from logger import logger


async def main():
    await database.connect()

    if config['testing']:
        await migration.drop_tables()
        await migration.run_migrations()
        await migration.fill_dummy_tables()
    else:
        try:
            await migration.run_migrations()
        except Exception:
            logger.warning("Migration script failed, dropping tables...")
            await migration.drop_tables()
            await migration.run_migrations()


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
