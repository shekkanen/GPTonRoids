import pytest
from fastapi.testclient import TestClient
from api.server import app
import os

client = TestClient(app)

@pytest.fixture(scope="module", autouse=True)
def setup_env():
    os.environ["API_KEY"] = "test_api_key"
    yield
    del os.environ["API_KEY"]

def test_write_new_file():
    response = client.put(
        "/files/new_test_file.txt",
        headers={"x-api-key": "test_api_key"},
        json={"content": "This is a new file."}
    )
    assert response.status_code == 200
    assert response.json()["message"] == "File written successfully"

def test_write_existing_file():
    # Create the initial file
    client.put(
        "/files/existing_test_file.txt",
        headers={"x-api-key": "test_api_key"},
        json={"content": "Original content."}
    )
    # Attempt to overwrite with different content
    response = client.put(
        "/files/existing_test_file.txt",
        headers={"x-api-key": "test_api_key"},
        json={"content": "Updated content."}
    )
    assert response.status_code == 200
    assert response.json()["message"] == "File written successfully"

def test_append_to_file():
        # Create the initial file
    client.put(
        "/files/append_test_file.txt",
        headers={"x-api-key": "test_api_key"},
        json={"content": "Initial content. "}
    )
    response = client.post(
        "/files/append_test_file.txt/append",
        headers={"x-api-key": "test_api_key"},
        json={"content": "Appended content."}
    )
    assert response.status_code == 200
    assert response.json()["message"] == "Content appended to 'append_test_file.txt' successfully"

    response = client.get("/files/append_test_file.txt", headers={"x-api-key": "test_api_key"})
    assert response.status_code == 200
    assert response.json() == "Initial content. Appended content."

def test_append_lines_to_file():
    # Create the initial file
    client.put(
        "/files/lines_test_file.txt",
        headers={"x-api-key": "test_api_key"},
        json={"content": "Initial content.\n"}
    )
    response = client.post(
            "/files/lines_test_file.txt/lines",
            headers={"x-api-key": "test_api_key"},
            json={"lines": ["Line 1", "Line 2"]}
        )
    assert response.status_code == 200
    assert response.json()["message"] == "Lines appended to 'lines_test_file.txt' successfully"

    response = client.get("/files/lines_test_file.txt", headers={"x-api-key": "test_api_key"})
    assert response.status_code == 200
    assert response.json() == "Initial content.\nLine 1\nLine 2\n"