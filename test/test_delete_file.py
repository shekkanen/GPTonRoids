import os
import pytest
from fastapi.testclient import TestClient
from api.server import app


client = TestClient(app)

@pytest.fixture(scope="module", autouse=True)
def setup_env():
    os.environ["API_KEY"] = "test_api_key"
    yield
    del os.environ["API_KEY"]

def test_delete_file():
    client.put("/files/test.txt", json={"content": "Hello, World!"}, headers={"x-api-key": "test_api_key"})
    response = client.delete("/files/test.txt", headers={"x-api-key": "test_api_key"})
    assert response.status_code == 200
    assert response.json() == {"message": "File deleted successfully"}