import pytest
from fastapi.testclient import TestClient
from prod.github_repo_endpoint import router

client = TestClient(router)

def test_get_issues():
    response = client.post(
        "/github-repo/issues",
        json={"owner": "owner_name", "repo": "repo_name"}
    )
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_create_issue():
    response = client.post(
        "/github-repo/issues/create",
        json={
            "owner": "owner_name",
            "repo": "repo_name",
            "title": "Test Issue Title",
            "body": "Test issue body content."
        }
    )
    assert response.status_code == 201
    issue = response.json()
    assert "issue_number" in issue
    assert "url" in issue