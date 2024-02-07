from fastapi import HTTPException
from .bot import Bot
from .bots import Bots
import pytest


class TestBot(Bot):
    pass


class TestBot_2(Bot):
    pass


@pytest.fixture()
def use_test_bots():
    old_bots = Bots.bots
    Bots.bots = {
        "test": TestBot,
        "test_2": TestBot_2
    }
    yield
    Bots.bots = old_bots


def test_parse_string_valid(use_test_bots):
    bots = Bots.parse_string("test: 5")
    assert len(bots) == 1
    assert bots[0][0] == "test"
    assert bots[0][1] == 5


def test_parse_string_valid_2(use_test_bots):
    bots = Bots.parse_string("test: 5; test_2: 1")
    assert len(bots) == 2
    assert bots[0][0] == "test"
    assert bots[0][1] == 5
    assert bots[1][0] == "test_2"
    assert bots[1][1] == 1


def test_parse_string_invalid(use_test_bots):
    with pytest.raises(HTTPException):
        Bots.parse_string("drummy: 5")

    with pytest.raises(HTTPException):
        Bots.parse_string("tes5")
    
    with pytest.raises(HTTPException):
        Bots.parse_string("test 5")
        
    with pytest.raises(HTTPException):
        Bots.parse_string("test: 5000")
        
    with pytest.raises(HTTPException):
        Bots.parse_string("test: -1")

    with pytest.raises(HTTPException):
        Bots.parse_string("test: 1;;")


def test_create_bots(use_test_bots):
    bots = Bots.create_bots("test: 4; test_2: 1")

    assert len(bots) == 5
    
    assert sum([isinstance(bot, TestBot) for bot in bots]) == 4
    assert sum([isinstance(bot, TestBot_2) for bot in bots]) == 1