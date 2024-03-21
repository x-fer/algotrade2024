from fastapi.testclient import TestClient
import pytest
import main
import uvicorn
from config import config

config["in_tests"] = True


client = TestClient(main.app)


@pytest.fixture(scope="session", autouse=True)
def setup():
    pass


def test_market():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello World"}
