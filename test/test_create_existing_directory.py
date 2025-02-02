import os
from dotenv import load_dotenv
import pytest
from fastapi.testclient import TestClient
from api.server import app

# Load environment variables from .env
load_dotenv()

client = TestClient(app)

@pytest.fixture(scope="module", autouse=True)
def setup_env():
    os.environ["GPTONROIDS_API_KEY"] = "test_GPTONROIDS_API_KEY"
    yield
    del os.environ["GPTONROIDS_API_KEY"]

def test_create_existing_directory():
    # Ensure the directory exists first
    client.post("/directories/existing_dir", headers={"GPTONROIDS_API_KEY": os.getenv("GPTONROIDS_API_KEY")})
    # Test creating the same directory again
    response = client.post("/directories/existing_dir", headers={"GPTONROIDS_API_KEY": os.getenv("GPTONROIDS_API_KEY")})
    assert response.status_code == 400
    assert response.json()["detail"] == "Directory already exists"
