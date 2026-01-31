"""
GitHub API client module for ghaly.

This module provides a high-level interface for interacting with the GitHub API,
including repository data retrieval, commit history, issues, and pull requests.
"""

from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import requests


class GitHubAPIError(Exception):
    """Exception raised for GitHub API errors."""
    pass


class GitHubRateLimitError(GitHubAPIError):
    """Exception raised when GitHub API rate limit is exceeded."""
    pass


class GitHubClient:
    """
    GitHub API client for making authenticated requests.
    
    Provides methods to fetch repository information, commits, issues,
    and pull requests with proper error handling and rate limit management.
    """
    
    def __init__(self, access_token: str, api_base_url: str = "https://api.github.com"):
        """
        Initialize GitHub API client.
        
        Args:
            access_token: GitHub OAuth access token
            api_base_url: GitHub API base URL
        """
        self.access_token = access_token
        self.api_base_url = api_base_url.rstrip('/')
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "ghaly/0.1.0"
        })
    
    def _make_request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Make authenticated request to GitHub API.
        
        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint path
            params: Query parameters
            data: Request body data
            
        Returns:
            Response JSON data
            
        Raises:
            GitHubAPIError: If request fails
            GitHubRateLimitError: If rate limit is exceeded
        """
        url = f"{self.api_base_url}{endpoint}"
        
        try:
            response = self.session.request(
                method=method,
                url=url,
                params=params,
                json=data
            )
            
            if response.status_code == 403:
                remaining = int(response.headers.get('X-RateLimit-Remaining', 0))
                if remaining == 0:
                    reset_time = int(response.headers.get('X-RateLimit-Reset', 0))
                    reset_datetime = datetime.fromtimestamp(reset_time)
                    raise GitHubRateLimitError(
                        f"GitHub API rate limit exceeded. "
                        f"Resets at {reset_datetime}"
                    )
            
            response.raise_for_status()
            
            if response.content:
                try:
                    return response.json()
                except ValueError:
                    return {}
            return {}
            
        except requests.HTTPError as e:
            if e.response is not None:
                try:
                    error_msg = e.response.json().get('message', str(e))
                except ValueError:
                    error_msg = str(e)
                raise GitHubAPIError(f"GitHub API error: {error_msg}")
            raise GitHubAPIError(f"HTTP error: {e}")
        except requests.RequestException as e:
            raise GitHubAPIError(f"Request failed: {e}")
    
    def get_repository(self, owner: str, repo: str) -> Dict[str, Any]:
        """
        Get repository information.
        
        Args:
            owner: Repository owner (username or organization)
            repo: Repository name
            
        Returns:
            Repository information dictionary
        """
        return self._make_request("GET", f"/repos/{owner}/{repo}")
    
    def get_commits(
        self,
        owner: str,
        repo: str,
        since: Optional[datetime] = None,
        until: Optional[datetime] = None,
        per_page: int = 100,
        max_pages: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Get commit history for a repository.
        
        Args:
            owner: Repository owner
            repo: Repository name
            since: Start date for commits
            until: End date for commits
            per_page: Number of results per page
            max_pages: Maximum number of pages to fetch
            
        Returns:
            List of commit dictionaries
        """
        params = {"per_page": per_page}
        
        if since:
            params["since"] = since.isoformat()
        if until:
            params["until"] = until.isoformat()
        
        commits = []
        page = 1
        
        while page <= max_pages:
            params["page"] = page
            response = self._make_request("GET", f"/repos/{owner}/{repo}/commits", params=params)
            
            if not response:
                break
            
            commits.extend(response)
            
            if len(response) < per_page:
                break
            
            page += 1
        
        return commits
    
    def get_issues(
        self,
        owner: str,
        repo: str,
        state: str = "all",
        since: Optional[datetime] = None,
        per_page: int = 100,
        max_pages: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Get issues for a repository.
        
        Args:
            owner: Repository owner
            repo: Repository name
            state: Issue state (open, closed, all)
            since: Start date for issues
            per_page: Number of results per page
            max_pages: Maximum number of pages to fetch
            
        Returns:
            List of issue dictionaries
        """
        params = {"state": state, "per_page": per_page}
        
        if since:
            params["since"] = since.isoformat()
        
        issues = []
        page = 1
        
        while page <= max_pages:
            params["page"] = page
            response = self._make_request("GET", f"/repos/{owner}/{repo}/issues", params=params)
            
            if not response:
                break
            
            issues.extend(response)
            
            if len(response) < per_page:
                break
            
            page += 1
        
        return issues
    
    def get_pull_requests(
        self,
        owner: str,
        repo: str,
        state: str = "all",
        since: Optional[datetime] = None,
        per_page: int = 100,
        max_pages: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Get pull requests for a repository.
        
        Args:
            owner: Repository owner
            repo: Repository name
            state: PR state (open, closed, all)
            since: Start date for PRs
            per_page: Number of results per page
            max_pages: Maximum number of pages to fetch
            
        Returns:
            List of pull request dictionaries
        """
        params = {"state": state, "per_page": per_page}
        
        if since:
            params["since"] = since.isoformat()
        
        prs = []
        page = 1
        
        while page <= max_pages:
            params["page"] = page
            response = self._make_request("GET", f"/repos/{owner}/{repo}/pulls", params=params)
            
            if not response:
                break
            
            prs.extend(response)
            
            if len(response) < per_page:
                break
            
            page += 1
        
        return prs
    
    def get_contributors(
        self,
        owner: str,
        repo: str,
        per_page: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Get contributors for a repository.
        
        Args:
            owner: Repository owner
            repo: Repository name
            per_page: Number of results per page
            
        Returns:
            List of contributor dictionaries
        """
        params = {"per_page": per_page}
        contributors = []
        page = 1
        
        while True:
            params["page"] = page
            response = self._make_request("GET", f"/repos/{owner}/{repo}/contributors", params=params)
            
            if not response:
                break
            
            contributors.extend(response)
            
            if len(response) < per_page:
                break
            
            page += 1
        
        return contributors
    
    def get_languages(self, owner: str, repo: str) -> Dict[str, int]:
        """
        Get programming languages used in a repository.
        
        Args:
            owner: Repository owner
            repo: Repository name
            
        Returns:
            Dictionary mapping language names to byte counts
        """
        return self._make_request("GET", f"/repos/{owner}/{repo}/languages")
    
    def get_stargazers_count(self, owner: str, repo: str) -> int:
        """
        Get the number of stargazers for a repository.
        
        Args:
            owner: Repository owner
            repo: Repository name
            
        Returns:
            Number of stargazers
        """
        repo_info = self.get_repository(owner, repo)
        return repo_info.get("stargazers_count", 0)
    
    def get_forks_count(self, owner: str, repo: str) -> int:
        """
        Get the number of forks for a repository.
        
        Args:
            owner: Repository owner
            repo: Repository name
            
        Returns:
            Number of forks
        """
        repo_info = self.get_repository(owner, repo)
        return repo_info.get("forks_count", 0)
    
    def get_repository_stats(
        self,
        owner: str,
        repo: str,
        days: int = 30
    ) -> Dict[str, Any]:
        """
        Get comprehensive repository statistics.
        
        Args:
            owner: Repository owner
            repo: Repository name
            days: Number of days to analyze
            
        Returns:
            Dictionary containing repository statistics
        """
        since_date = datetime.utcnow() - timedelta(days=days)
        
        commits = self.get_commits(owner, repo, since=since_date)
        issues = self.get_issues(owner, repo, since=since_date)
        prs = self.get_pull_requests(owner, repo, since=since_date)
        contributors = self.get_contributors(owner, repo)
        languages = self.get_languages(owner, repo)
        
        repo_info = self.get_repository(owner, repo)
        
        return {
            "repository": repo_info,
            "commits": {
                "total": len(commits),
                "recent": commits
            },
            "issues": {
                "total": len(issues),
                "open": len([i for i in issues if i["state"] == "open"]),
                "closed": len([i for i in issues if i["state"] == "closed"]),
                "recent": issues
            },
            "pull_requests": {
                "total": len(prs),
                "open": len([p for p in prs if p["state"] == "open"]),
                "merged": len([p for p in prs if p.get("merged_at")]),
                "recent": prs
            },
            "contributors": {
                "total": len(contributors),
                "recent": contributors[:10]
            },
            "languages": languages,
            "stargazers": repo_info.get("stargazers_count", 0),
            "forks": repo_info.get("forks_count", 0),
            "created_at": repo_info.get("created_at"),
            "updated_at": repo_info.get("updated_at"),
            "pushed_at": repo_info.get("pushed_at")
        }
