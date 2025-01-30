import os  # Add this import
import pytest
from fastapi.testclient import TestClient
from api.server import app
from unittest.mock import MagicMock

client = TestClient(app)

@pytest.fixture(scope="module", autouse=True)
def setup_env():
    # Set the API_KEY environment variable for the duration of the tests
    os.environ["API_KEY"] = "test_api_key"
    yield
    # Clean up after tests
    del os.environ["API_KEY"]

def mock_get_github_client():
    """Mock the GitHub client to avoid actual API calls."""
    mock_repo = MagicMock()
    mock_repo.name = "repo_name"
    mock_repo.full_name = "owner_name/repo_name"
    mock_repo.description = "Test repository"
    mock_repo.clone_url = "https://github.com/owner_name/repo_name.git"
    mock_repo.stargazers_count = 10
    mock_repo.forks_count = 2
    mock_repo.open_issues_count = 1
    
    mock_issue = MagicMock()
    mock_issue.number = 1
    mock_issue.title = "Test Issue Title"
    mock_issue.body = "Test issue body content."
    mock_issue.state = "open"
    mock_issue.created_at.isoformat.return_value = "2025-01-01T00:00:00Z"
    mock_issue.updated_at.isoformat.return_value = "2025-01-01T00:00:00Z"
    mock_issue.html_url = "https://github.com/owner_name/repo_name/issues/1"
    
    mock_repo.create_issue.return_value = mock_issue
    mock_repo.get_issues.return_value = [mock_issue]
    
    mock_github = MagicMock()
    mock_github.get_repo.return_value = mock_repo
    
    return mock_github

@pytest.fixture
def mock_github_client(mocker):
    """Fixture to mock the GitHub client."""
    mocker.patch("api.github_repo_endpoint.get_github_client", return_value=mock_get_github_client())

def test_get_issues(mock_github_client):
    response = client.post(
        "/github-repo/issues",
        json={"owner": "owner_name", "repo": "repo_name"},
        headers={"x-api-key": "test_api_key"}
    )
    assert response.status_code == 200
    issues = response.json()
    assert isinstance(issues, list)
    assert len(issues) == 1
    issue = issues[0]
    assert issue["issue_number"] == 1
    assert issue["title"] == "Test Issue Title"
    assert issue["url"] == "https://github.com/owner_name/repo_name/issues/1"

def test_create_issue(mock_github_client):
    response = client.post(
        "/github-repo/issues/create",
        json={
            "owner": "owner_name",
            "repo": "repo_name",
            "title": "Test Issue Title",
            "body": "Test issue body content."
        },
        headers={"x-api-key": "test_api_key"}
    )
    assert response.status_code == 200  # Adjusted to 200 based on FastAPI defaults
    issue = response.json()
    assert issue["issue_number"] == 1
    assert issue["title"] == "Test Issue Title"
    assert issue["url"] == "https://github.com/owner_name/repo_name/issues/1"
