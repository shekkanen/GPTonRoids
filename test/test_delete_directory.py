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

def test_delete_directory():
    client.post("/directories/test_dir", headers={"GPTONROIDS_API_KEY": "test_GPTONROIDS_API_KEY"})
    response = client.delete("/directories/test_dir", headers={"GPTONROIDS_API_KEY": "test_GPTONROIDS_API_KEY"})
    assert response.status_code == 200
    assert response.json() == {"message": "Directory 'test_dir' deleted successfully"}
