import os
from dotenv import load_dotenv
import pytest
from fastapi.testclient import TestClient
from dev.server import app

# Load environment variables from .env
load_dotenv()

client = TestClient(app)

@pytest.fixture(scope="module", autouse=True)
def setup_env():
    os.environ["API_KEY"] = "test_api_key"
    yield
    del os.environ["API_KEY"]

def test_create_directory():
    response = client.post("/directories/test_dir", headers={"x-api-key": os.getenv("API_KEY")})
    assert response.status_code == 200
    assert response.json() == {"message": "Directory 'test_dir' created successfully"}
