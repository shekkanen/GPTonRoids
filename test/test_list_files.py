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

def test_list_files():
    response = client.get("/directories/", headers={"x-api-key": "test_api_key"})
    assert response.status_code == 200
    assert isinstance(response.json()["files"], list)