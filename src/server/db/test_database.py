import pytest
from databases import Database
from db import Table
from db import Team
from db import database
from config import config


@pytest.fixture
async def connect_db():
    Table.set_db(database)
    await database.connect()
    yield database
    await database.disconnect()

@pytest.mark.asyncio
async def test_create_and_get_team(connect_db):
    team_data = {
        "team_name": "Sample Team",
        "team_secret": "secretpassword"
    }

    created_team_id = await Team.create(**team_data)
    retrieved_team = await Team.get(team_id=created_team_id)

    assert retrieved_team.team_id == 0
    assert retrieved_team.team_name == team_data["team_name"]
    assert retrieved_team.team_secret == team_data["team_secret"]
