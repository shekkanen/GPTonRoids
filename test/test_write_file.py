import pytest
from fastapi.testclient import TestClient
from dev.server import app
import os

client = TestClient(app)

@pytest.fixture(scope="module", autouse=True)
def setup_env():
    os.environ["API_KEY"] = "test_api_key"
    yield
    del os.environ["API_KEY"]

def test_write_new_file():
    response = client.post(
        "/files",
        headers={"x-api-key": "test_api_key"},
        json={"filename": "new_test_file.txt", "content": "This is a new file."}
    )
    assert response.status_code == 201
    assert response.json()["message"] == "File written successfully"

def test_write_existing_file_with_diff():
    # Create the initial file
    client.post(
        "/files",
        headers={"x-api-key": "test_api_key"},
        json={"filename": "existing_test_file.txt", "content": "Original content."}
    )
    # Attempt to overwrite with different content
    response = client.post(
        "/files",
        headers={"x-api-key": "test_api_key"},
        json={"filename": "existing_test_file.txt", "content": "Updated content."}
    )
    if response.status_code == 400:  # Rejected by AIJudge
        assert "Changes rejected by AIJudge" in response.json()["message"]
    else:  # Approved by AIJudge
        assert response.status_code == 201
        assert response.json()["message"] == "File written successfully"

def test_ai_judge_rejects_write():
    # Create the initial file with important lines
    client.post(
        "/files",
        headers={"x-api-key": "test_api_key"},
        json={"filename": "critical_file.txt", "content": "Important line 1\nImportant line 2"}
    )
    # Attempt to overwrite with destructive content
    response = client.post(
        "/files",
        headers={"x-api-key": "test_api_key"},
        json={"filename": "critical_file.txt", "content": "New line 1\nNew line 2"}
    )
    assert response.status_code == 400
    assert "Changes rejected by AIJudge" in response.json()["message"]
