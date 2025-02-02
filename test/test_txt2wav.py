
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

def test_txt2wav():
    try:
        response = client.post(
            "/txt2wav",
            json={"text": "Hello, World!"},
            headers={"GPTONROIDS_API_KEY": "test_GPTONROIDS_API_KEY"},
            timeout=10  # Timeout after 10 seconds
        )
        assert response.status_code == 200
        assert "filename" in response.json()
    except Exception as e:
        pytest.fail(f"Test timed out or failed: {e}")
