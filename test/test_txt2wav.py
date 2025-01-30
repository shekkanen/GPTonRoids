
import os
import pytest
from fastapi.testclient import TestClient
from dev.server import app


client = TestClient(app)

@pytest.fixture(scope="module", autouse=True)
def setup_env():
    os.environ["API_KEY"] = "test_api_key"
    yield
    del os.environ["API_KEY"]

def test_txt2wav():
    try:
        response = client.post(
            "/txt2wav",
            json={"text": "Hello, World!"},
            headers={"x-api-key": "test_api_key"},
            timeout=10  # Timeout after 10 seconds
        )
        assert response.status_code == 200
        assert "filename" in response.json()
    except Exception as e:
        pytest.fail(f"Test timed out or failed: {e}")
