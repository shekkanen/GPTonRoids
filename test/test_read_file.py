import os
import pytest
from fastapi.testclient import TestClient
from api.server import app


client = TestClient(app)

@pytest.fixture(scope="module", autouse=True)
def setup_env():
    os.environ["GPTONROIDS_API_KEY"] = "test_GPTONROIDS_API_KEY"
    yield
    del os.environ["GPTONROIDS_API_KEY"]

def test_read_file():
    client.put("/files/test.txt", json={"content": "Hello, World!"}, headers={"GPTONROIDS_API_KEY": "test_GPTONROIDS_API_KEY"})
    response = client.get("/files/test.txt", headers={"GPTONROIDS_API_KEY": "test_GPTONROIDS_API_KEY"})
    assert response.status_code == 200
    assert response.json() == "Hello, World!"