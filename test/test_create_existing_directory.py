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
    os.environ["API_KEY"] = "test_api_key"
    yield
    del os.environ["API_KEY"]

def test_create_existing_directory():
    # Ensure the directory exists first
    client.post("/directories/existing_dir", headers={"x-api-key": os.getenv("API_KEY")})
    # Test creating the same directory again
    response = client.post("/directories/existing_dir", headers={"x-api-key": os.getenv("API_KEY")})
    assert response.status_code == 400
    assert response.json()["detail"] == "Directory already exists"
