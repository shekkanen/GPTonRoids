import os
import pytest
from fastapi.testclient import TestClient
from dev.server import app

client = TestClient(app)

# Mocked response data
mock_repo_info = {
    "name": "Hello-World",
    "full_name": "octocat/Hello-World",
    "description": "This is a mock repository for testing.",
    "clone_url": "https://github.com/octocat/Hello-World.git",
    "stargazers_count": 42,
    "forks_count": 7,
    "open_issues_count": 1,
}

@pytest.fixture(scope="module", autouse=True)
def setup_env():
    os.environ["API_KEY"] = "test_api_key"
    os.environ["GITHUB_TOKEN"] = "your-github-token"  # Add GitHub token for testing
    yield
    del os.environ["API_KEY"]
    del os.environ["GITHUB_TOKEN"]

@pytest.fixture(scope="function", autouse=True)
def mock_github_get_repo(mocker):
    """Mocks the GitHub client."""
    mock_repo = mocker.Mock()
    mock_repo.name = mock_repo_info["name"]
    mock_repo.full_name = mock_repo_info["full_name"]
    mock_repo.description = mock_repo_info["description"]
    mock_repo.clone_url = mock_repo_info["clone_url"]
    mock_repo.stargazers_count = mock_repo_info["stargazers_count"]
    mock_repo.forks_count = mock_repo_info["forks_count"]
    mock_repo.open_issues_count = mock_repo_info["open_issues_count"]

    mock_github = mocker.Mock()
    mock_github.get_repo.return_value = mock_repo

    mocker.patch("dev.github_repo_endpoint.get_github_client", return_value=mock_github)

def test_get_github_repo_info():
    """Test the `/github-repo` endpoint with mocked GitHub API."""
    response = client.post(
        "/github-repo",
        json={"owner": "octocat", "repo": "Hello-World"},
        headers={"x-api-key": "test_api_key"}
    )
    assert response.status_code == 200
    assert response.json() == mock_repo_info

def test_list_files():
    response = client.get("/files", headers={"x-api-key": "test_api_key"})
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_write_file():
    response = client.post("/files", json={"filename": "test.txt", "content": "Hello, World!"}, headers={"x-api-key": "test_api_key"})
    assert response.status_code == 201
    assert response.json() == {"message": "File written successfully"}

def test_read_file():
    client.post("/files", json={"filename": "test.txt", "content": "Hello, World!"}, headers={"x-api-key": "test_api_key"})
    response = client.get("/files/test.txt", headers={"x-api-key": "test_api_key"})
    assert response.status_code == 200
    assert response.json() == "Hello, World!"  # Adjusted to parse response JSON

def test_delete_file():
    client.post("/files", json={"filename": "test.txt", "content": "Hello, World!"}, headers={"x-api-key": "test_api_key"})
    response = client.delete("/files/test.txt", headers={"x-api-key": "test_api_key"})
    assert response.status_code == 200
    assert response.json() == {"message": "File deleted successfully"}

def test_create_directory():
    response = client.post("/directories/test_dir", headers={"x-api-key": "test_api_key"})
    assert response.status_code == 200
    assert response.json() == {"message": "Directory 'test_dir' created successfully"}

def test_delete_directory():
    client.post("/directories/test_dir", headers={"x-api-key": "test_api_key"})
    response = client.delete("/directories/test_dir", headers={"x-api-key": "test_api_key"})
    assert response.status_code == 200
    assert response.json() == {"message": "Directory 'test_dir' deleted successfully"}

def test_run_command():
    response = client.post("/run-command", json={"command": "echo Hello"}, headers={"x-api-key": "test_api_key"})
    assert response.status_code == 200
    assert response.json()["stdout"] == "Hello"

# def test_txt2wav():
#     response = client.post("/txt2wav", json={"text": "Hello, World!"}, headers={"x-api-key": "test_api_key"})
#     assert response.status_code == 200
#     assert "filename" in response.json()

# def test_get_screenshot():
#     response = client.get("/screenshot", headers={"x-api-key": "test_api_key"})
#     assert response.status_code == 200
#     assert "file_path" in response.json()

# def test_upload_file():
#     file_content = b"Hello, World!"
#     response = client.post("/upload-file", files={"file": ("test_upload.txt", file_content)}, headers={"x-api-key": "test_api_key"})
#     assert response.status_code == 200
#     assert response.json()["info"].startswith("file 'test_upload.txt' saved at")

# def test_search_files():
#     client.post("/files", json={"filename": "search_test.txt", "content": "This is a test file."}, headers={"x-api-key": "test_api_key"})
#     response = client.post("/search-files", json={"query": "test"}, headers={"x-api-key": "test_api_key"})
#     assert response.status_code == 200
#     assert any("search_test.txt" in match for match in response.json()["matches"])

# def test_get_file_metadata():
#     client.post("/files", json={"filename": "metadata_test.txt", "content": "Metadata test content."}, headers={"x-api-key": "test_api_key"})
#     response = client.get("/file-metadata/metadata_test.txt", headers={"x-api-key": "test_api_key"})
#     assert response.status_code == 200
#     metadata = response.json()
#     assert metadata["filename"] == "metadata_test.txt"
#     assert "size" in metadata
#     assert "created" in metadata
#     assert "modified" in metadata

# def test_get_github_repo_info():
#     response = client.post("/github-repo", json={"owner": "octocat", "repo": "Hello-World"}, headers={"x-api-key": "test_api_key"})
#     assert response.status_code == 200
#     repo_info = response.json()
#     assert "name" in repo_info
#     assert "full_name" in repo_info
#     assert "description" in repo_info
#     assert "clone_url" in repo_info
#     assert "stargazers_count" in repo_info
#     assert "forks_count" in repo_info
#     assert "open_issues_count" in repo_info
