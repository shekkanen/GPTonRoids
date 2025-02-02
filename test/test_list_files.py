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

def test_list_files():
    response = client.get("/directories/", headers={"GPTONROIDS_API_KEY": "test_GPTONROIDS_API_KEY"})
    assert response.status_code == 200
    assert isinstance(response.json()["files"], list)