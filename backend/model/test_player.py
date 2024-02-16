import pytest
from model import Player


@pytest.fixture
def sample_player():
    return Player(
        player_id=1,
        player_name="John",
        game_id=1,
        team_id=1
    )


def test_player_initialization(sample_player):
    assert sample_player.player_id == 1
    assert sample_player.player_name == "John"
    assert sample_player.game_id == 1
    assert sample_player.team_id == 1
    assert sample_player.is_active is True
    assert sample_player.is_bot is False
    assert sample_player.energy_price == 1e9
    assert sample_player.money == 0
    assert sample_player.energy == 0
    assert sample_player.coal == 0
    assert sample_player.uranium == 0
    assert sample_player.biomass == 0
    assert sample_player.gas == 0
    assert sample_player.oil == 0


def test_player_indexing(sample_player):
    sample_player['money'] = 100
    sample_player['energy'] = 50
    sample_player['coal'] = 20
    sample_player['uranium'] = 10
    sample_player['biomass'] = 5
    sample_player['gas'] = 30
    sample_player['oil'] = 25

    assert sample_player.money == 100
    assert sample_player.energy == 50
    assert sample_player.coal == 20
    assert sample_player.uranium == 10
    assert sample_player.biomass == 5
    assert sample_player.gas == 30
    assert sample_player.oil == 25


def test_player_getitem(sample_player):
    sample_player['money'] = 100
    assert sample_player['money'] == 100

    sample_player['energy'] = 50
    assert sample_player['energy'] == 50

    sample_player['coal'] = 20
    assert sample_player['coal'] == 20

    sample_player['uranium'] = 10
    assert sample_player['uranium'] == 10

    sample_player['biomass'] = 5
    assert sample_player['biomass'] == 5

    sample_player['gas'] = 30
    assert sample_player['gas'] == 30

    sample_player['oil'] = 25
    assert sample_player['oil'] == 25
