import pytest
from db import database, migration
from model import Team
from config import config
import pytest_asyncio


@pytest_asyncio.fixture(autouse=True)
async def delete_db():
    await database.connect()
    yield database
    await migration.delete_tables()
    await database.disconnect()


@pytest_asyncio.fixture(scope="session", autouse=True)
async def connect_db():
    await database.connect()
    await migration.drop_tables()
    await migration.run_migrations()
    await database.disconnect()
    return


@pytest.mark.asyncio
async def test_create_and_get_team():
    assert len(await Team.list()) == 0
    team_data = {
        "team_name": "Sample Team",
        "team_secret": "secretpassword"
    }
    created_team_id = await Team.create(**team_data)
    retrieved_team = await Team.get(team_id=created_team_id)

    assert retrieved_team.team_name == team_data["team_name"]
    assert retrieved_team.team_secret == team_data["team_secret"]


@pytest.mark.asyncio
async def test_create_and_get_team_2():
    assert len(await Team.list()) == 0
    team_data = {
        "team_name": "Sample Team",
        "team_secret": "secretpassword"
    }
    created_team_id = await Team.create(**team_data)
    retrieved_team = await Team.get(team_id=created_team_id)

    assert retrieved_team.team_name == team_data["team_name"]
    assert retrieved_team.team_secret == team_data["team_secret"]
