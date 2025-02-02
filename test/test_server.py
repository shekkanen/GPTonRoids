import os
import pytest
from fastapi.testclient import TestClient
from api.server import app

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
    os.environ["GPTONROIDS_API_KEY"] = "test_GPTONROIDS_API_KEY"
    os.environ["GITHUB_TOKEN"] = "your-github-token"  # Add GitHub token for testing
    yield
    del os.environ["GPTONROIDS_API_KEY"]
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

    mocker.patch("api.github_repo_endpoint.get_github_client", return_value=mock_github)

def test_get_github_repo_info():
    """Test the `/github-repo` endpoint with mocked GitHub API."""
    response = client.post(
        "/github-repo",
        json={"owner": "octocat", "repo": "Hello-World"},
        headers={"GPTONROIDS_API_KEY": "test_GPTONROIDS_API_KEY"}
    )
    assert response.status_code == 200
    assert response.json() == mock_repo_info

def test_list_files():
    response = client.get("/directories/", headers={"GPTONROIDS_API_KEY": "test_GPTONROIDS_API_KEY"})
    assert response.status_code == 200
    assert isinstance(response.json()["files"], list)

def test_write_file():
    response = client.put("/files/test.txt", json={"content": "Hello, World!"}, headers={"GPTONROIDS_API_KEY": "test_GPTONROIDS_API_KEY"})
    assert response.status_code == 200
    assert response.json() == {"message": "File written successfully"}

def test_read_file():
    client.put("/files/test.txt", json={"content": "Hello, World!"}, headers={"GPTONROIDS_API_KEY": "test_GPTONROIDS_API_KEY"})
    response = client.get("/files/test.txt", headers={"GPTONROIDS_API_KEY": "test_GPTONROIDS_API_KEY"})
    assert response.status_code == 200
    assert response.json() == "Hello, World!"  # Adjusted to parse response JSON

def test_delete_file():
    client.put("/files/test.txt", json={"content": "Hello, World!"}, headers={"GPTONROIDS_API_KEY": "test_GPTONROIDS_API_KEY"})
    response = client.delete("/files/test.txt", headers={"GPTONROIDS_API_KEY": "test_GPTONROIDS_API_KEY"})
    assert response.status_code == 200
    assert response.json() == {"message": "File deleted successfully"}

def test_create_directory():
    response = client.post("/directories/test_dir", headers={"GPTONROIDS_API_KEY": "test_GPTONROIDS_API_KEY"})
    assert response.status_code == 200
    assert response.json() == {"message": "Directory 'test_dir' created successfully"}

def test_delete_directory():
    client.post("/directories/test_dir", headers={"GPTONROIDS_API_KEY": "test_GPTONROIDS_API_KEY"})
    response = client.delete("/directories/test_dir", headers={"GPTONROIDS_API_KEY": "test_GPTONROIDS_API_KEY"})
    assert response.status_code == 200
    assert response.json() == {"message": "Directory 'test_dir' deleted successfully"}

def test_run_command():
    response = client.post(
        "/run-command",
        json={"command": "echo Hello", "plan": "testing"},
        headers={"GPTONROIDS_API_KEY": "test_GPTONROIDS_API_KEY"}
    )
    assert response.status_code == 200
    assert response.json()["stdout"] == "Hello"