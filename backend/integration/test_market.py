from fastapi.testclient import TestClient
import pytest
import main
import uvicorn
from config import config

config["in_tests"] = True


def get_client():
    with TestClient(main.app) as client:
        while True:
            yield client


@pytest.fixture(scope="session", autouse=True)
def setup():
    pass


def test_market():
    client = get_client()

    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello World"}
