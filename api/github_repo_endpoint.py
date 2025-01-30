from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from github import Github, Auth
import os

from api.config import get_api_key, logger

router = APIRouter()

# Models
class GitHubRepoRequest(BaseModel):
    owner: str
    repo: str

class GitHubIssueRequest(GitHubRepoRequest):
    issue_number: int

class CreateIssueRequest(GitHubRepoRequest):
    title: str
    body: str

# Helper: GitHub Client
def get_github_client():
    token = os.getenv("GITHUB_TOKEN")
    if not token:
        raise HTTPException(status_code=500, detail="GitHub token not set in environment variables")
    return Github(auth=Auth.Token(token))

# Fetch GitHub Repo Info
@router.post("/github-repo", dependencies=[Depends(get_api_key)])
async def get_github_repo_info(request: GitHubRepoRequest):
    try:
        g = get_github_client()
        repo = g.get_repo(f"{request.owner}/{request.repo}")
        return {
            "name": repo.name,
            "full_name": repo.full_name,
            "description": repo.description,
            "clone_url": repo.clone_url,
            "stargazers_count": repo.stargazers_count,
            "forks_count": repo.forks_count,
            "open_issues_count": repo.open_issues_count,
        }
    except Exception as e:
        logger.error(f"Failed to fetch repo info: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to fetch repo info: {str(e)}")

# Fetch GitHub Issues
@router.post("/github-repo/issues", dependencies=[Depends(get_api_key)])
async def get_github_repo_issues(request: GitHubRepoRequest):
    try:
        g = get_github_client()
        repo = g.get_repo(f"{request.owner}/{request.repo}")
        issues = repo.get_issues(state='open')  # Fetch all open issues
        return [
            {
                "issue_number": issue.number,
                "title": issue.title,
                "state": issue.state,
                "created_at": issue.created_at.isoformat(),
                "updated_at": issue.updated_at.isoformat(),
                "url": issue.html_url,
            }
            for issue in issues
        ]
    except Exception as e:
        logger.error(f"Failed to fetch issues: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to fetch issues: {str(e)}")

# Fetch GitHub Issue Details
@router.post("/github-repo/issues/detail", dependencies=[Depends(get_api_key)])
async def get_github_issue_detail(request: GitHubIssueRequest):
    try:
        g = get_github_client()
        repo = g.get_repo(f"{request.owner}/{request.repo}")
        issue = repo.get_issue(number=request.issue_number)
        return {
            "issue_number": issue.number,
            "title": issue.title,
            "body": issue.body,
            "state": issue.state,
            "created_at": issue.created_at.isoformat(),
            "updated_at": issue.updated_at.isoformat(),
            "url": issue.html_url,
        }
    except Exception as e:
        logger.error(f"Failed to fetch issue details: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to fetch issue details: {str(e)}")

# Create GitHub Issue
@router.post("/github-repo/issues/create", dependencies=[Depends(get_api_key)])
async def create_github_issue(request: CreateIssueRequest):
    try:
        g = get_github_client()
        repo = g.get_repo(f"{request.owner}/{request.repo}")
        new_issue = repo.create_issue(title=request.title, body=request.body)
        return {
            "issue_number": new_issue.number,
            "title": new_issue.title,
            "state": new_issue.state,
            "created_at": new_issue.created_at.isoformat(),
            "updated_at": new_issue.updated_at.isoformat(),
            "url": new_issue.html_url,
        }
    except Exception as e:
        logger.error(f"Failed to create issue: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to create issue: {str(e)}")
