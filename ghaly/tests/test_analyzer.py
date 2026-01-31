"""
Unit tests for ghaly analyzer.
"""

from datetime import datetime, timedelta
from unittest.mock import Mock, patch

import pytest

from ghaly.analyzer import HealthStatus, RepositoryAnalyzer


@pytest.fixture
def mock_github_client():
    """Create a mock GitHub client."""
    client = Mock()
    return client


@pytest.fixture
def sample_repo_stats():
    """Sample repository statistics."""
    return {
        "repository": {
            "name": "test-repo",
            "description": "A test repository",
            "language": "Python",
            "stargazers_count": 100,
            "forks_count": 50,
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-15T00:00:00Z",
            "pushed_at": "2024-01-15T00:00:00Z"
        },
        "commits": {
            "total": 30,
            "recent": [
                {"sha": "abc123", "commit": {"author": {"login": "user1"}}},
                {"sha": "def456", "commit": {"author": {"login": "user2"}}}
            ]
        },
        "issues": {
            "total": 20,
            "open": 5,
            "closed": 15,
            "recent": [
                {"state": "open", "created_at": "2024-01-10T00:00:00Z"},
                {"state": "closed", "created_at": "2024-01-05T00:00:00Z", "closed_at": "2024-01-07T00:00:00Z"}
            ]
        },
        "pull_requests": {
            "total": 10,
            "open": 2,
            "merged": 7,
            "recent": [
                {"state": "open", "created_at": "2024-01-12T00:00:00Z"},
                {"state": "closed", "merged_at": "2024-01-08T00:00:00Z"}
            ]
        },
        "contributors": {
            "total": 10,
            "recent": [
                {"login": "user1", "contributions": 100},
                {"login": "user2", "contributions": 80},
                {"login": "user3", "contributions": 60}
            ]
        },
        "languages": {
            "Python": 10000,
            "JavaScript": 5000
        },
        "stargazers": 100,
        "forks": 50,
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-15T00:00:00Z",
        "pushed_at": "2024-01-15T00:00:00Z"
    }


class TestRepositoryAnalyzer:
    """Test cases for RepositoryAnalyzer class."""
    
    def test_init(self, mock_github_client):
        """Test initialization."""
        config = {"activity_days": 30, "health_thresholds": {"active": 10, "moderate": 5}}
        analyzer = RepositoryAnalyzer(mock_github_client, config)
        
        assert analyzer.client == mock_github_client
        assert analyzer.activity_days == 30
        assert analyzer.thresholds == {"active": 10, "moderate": 5}
    
    def test_init_default_config(self, mock_github_client):
        """Test initialization with default config."""
        analyzer = RepositoryAnalyzer(mock_github_client)
        
        assert analyzer.activity_days == 30
        assert analyzer.thresholds == {"active": 10, "moderate": 5}
    
    def test_analyze_repository(self, mock_github_client, sample_repo_stats):
        """Test repository analysis."""
        mock_github_client.get_repository_stats.return_value = sample_repo_stats
        
        analyzer = RepositoryAnalyzer(mock_github_client)
        result = analyzer.analyze_repository("test-owner", "test-repo")
        
        assert "repository" in result
        assert "metrics" in result
        assert "health" in result
        assert "languages" in result
        assert "contributors" in result
        
        assert result["repository"]["name"] == "test-repo"
        assert result["repository"]["language"] == "Python"
    
    def test_calculate_commit_frequency(self, mock_github_client, sample_repo_stats):
        """Test commit frequency calculation."""
        analyzer = RepositoryAnalyzer(mock_github_client)
        
        commits = sample_repo_stats["commits"]["recent"]
        commit_freq = analyzer._calculate_commit_frequency(commits)
        
        assert commit_freq["total"] == 2
        assert commit_freq["per_day"] == round(2 / 30, 2)
        assert commit_freq["per_week"] == round(2 / 30 * 7, 2)
        assert commit_freq["per_month"] == round(2 / 30 * 30, 2)
    
    def test_calculate_issue_activity(self, mock_github_client, sample_repo_stats):
        """Test issue activity calculation."""
        analyzer = RepositoryAnalyzer(mock_github_client)
        
        issues = sample_repo_stats["issues"]["recent"]
        issue_activity = analyzer._calculate_issue_activity(issues)
        
        assert issue_activity["total"] == 2
        assert issue_activity["open"] == 1
        assert issue_activity["closed"] == 1
    
    def test_calculate_pr_activity(self, mock_github_client, sample_repo_stats):
        """Test PR activity calculation."""
        analyzer = RepositoryAnalyzer(mock_github_client)
        
        prs = sample_repo_stats["pull_requests"]["recent"]
        pr_activity = analyzer._calculate_pr_activity(prs)
        
        assert pr_activity["total"] == 2
        assert pr_activity["open"] == 1
        assert pr_activity["merged"] == 1
    
    def test_calculate_contributor_activity(self, mock_github_client, sample_repo_stats):
        """Test contributor activity calculation."""
        analyzer = RepositoryAnalyzer(mock_github_client)
        
        contributors = sample_repo_stats["contributors"]["recent"]
        contrib_activity = analyzer._calculate_contributor_activity(contributors)
        
        assert contrib_activity["total"] == 3
        assert len(contrib_activity["top_contributors"]) == 3
    
    def test_calculate_code_velocity_high(self, mock_github_client):
        """Test code velocity calculation for high activity."""
        analyzer = RepositoryAnalyzer(mock_github_client)
        
        commits = [{"sha": str(i)} for i in range(150)]
        metrics = analyzer._calculate_code_velocity(commits)
        
        assert metrics["velocity"] == "high"
    
    def test_calculate_code_velocity_medium(self, mock_github_client):
        """Test code velocity calculation for medium activity."""
        analyzer = RepositoryAnalyzer(mock_github_client)
        
        commits = [{"sha": str(i)} for i in range(60)]
        metrics = analyzer._calculate_code_velocity(commits)
        
        assert metrics["velocity"] == "medium"
    
    def test_calculate_code_velocity_low(self, mock_github_client):
        """Test code velocity calculation for low activity."""
        analyzer = RepositoryAnalyzer(mock_github_client)
        
        commits = [{"sha": str(i)} for i in range(10)]
        metrics = analyzer._calculate_code_velocity(commits)
        
        assert metrics["velocity"] == "low"
    
    def test_calculate_community_engagement(self, mock_github_client, sample_repo_stats):
        """Test community engagement calculation."""
        analyzer = RepositoryAnalyzer(mock_github_client)
        
        metrics = analyzer._calculate_metrics(sample_repo_stats)
        
        engagement = metrics["community_engagement"]
        
        assert engagement["stars"] == 100
        assert engagement["forks"] == 50
        assert engagement["engagement_score"] > 0
        assert engagement["level"] in ["very_high", "high", "moderate", "low", "very_low"]
    
    def test_calculate_health_score_active(self, mock_github_client):
        """Test health score calculation for active repository."""
        analyzer = RepositoryAnalyzer(mock_github_client)
        
        metrics = {
            "commit_frequency": {"per_day": 10},
            "issue_activity": {"total": 10, "close_rate": 80},
            "pr_activity": {"total": 5, "merge_rate": 90},
            "contributor_activity": {"total": 15},
            "community_engagement": {"level": "high"}
        }
        
        health = analyzer._calculate_health(metrics)
        
        assert health["score"] >= 70
        assert health["status"] == "active"
    
    def test_calculate_health_score_moderate(self, mock_github_client):
        """Test health score calculation for moderate repository."""
        analyzer = RepositoryAnalyzer(mock_github_client)
        
        metrics = {
            "commit_frequency": {"per_day": 2},
            "issue_activity": {"total": 5, "close_rate": 60},
            "pr_activity": {"total": 2, "merge_rate": 70},
            "contributor_activity": {"total": 3},
            "community_engagement": {"level": "moderate"}
        }
        
        health = analyzer._calculate_health(metrics)
        
        assert 40 <= health["score"] < 70
        assert health["status"] == "moderate"
    
    def test_calculate_health_score_inactive(self, mock_github_client):
        """Test health score calculation for inactive repository."""
        analyzer = RepositoryAnalyzer(mock_github_client)
        
        metrics = {
            "commit_frequency": {"per_day": 0.1},
            "issue_activity": {"total": 0, "close_rate": 0},
            "pr_activity": {"total": 0, "merge_rate": 0},
            "contributor_activity": {"total": 1},
            "community_engagement": {"level": "very_low"}
        }
        
        health = analyzer._calculate_health(metrics)
        
        assert health["score"] < 40
        assert health["status"] == "inactive"
    
    def test_score_commits_high(self, mock_github_client):
        """Test commit scoring for high activity."""
        analyzer = RepositoryAnalyzer(mock_github_client)
        
        commit_freq = {"per_day": 10}
        score = analyzer._score_commits(commit_freq)
        
        assert score == 100
    
    def test_score_commits_low(self, mock_github_client):
        """Test commit scoring for low activity."""
        analyzer = RepositoryAnalyzer(mock_github_client)
        
        commit_freq = {"per_day": 0.1}
        score = analyzer._score_commits(commit_freq)
        
        assert score == 20
    
    def test_score_issues(self, mock_github_client):
        """Test issue scoring."""
        analyzer = RepositoryAnalyzer(mock_github_client)
        
        issue_activity = {"total": 10, "close_rate": 80}
        score = analyzer._score_issues(issue_activity)
        
        assert 0 <= score <= 100
    
    def test_score_prs(self, mock_github_client):
        """Test PR scoring."""
        analyzer = RepositoryAnalyzer(mock_github_client)
        
        pr_activity = {"total": 5, "merge_rate": 90}
        score = analyzer._score_prs(pr_activity)
        
        assert 0 <= score <= 100
    
    def test_score_contributors(self, mock_github_client):
        """Test contributor scoring."""
        analyzer = RepositoryAnalyzer(mock_github_client)
        
        contrib_activity = {"total": 15}
        score = analyzer._score_contributors(contrib_activity)
        
        assert score == 100
    
    def test_score_engagement(self, mock_github_client):
        """Test engagement scoring."""
        analyzer = RepositoryAnalyzer(mock_github_client)
        
        engagement = {"level": "high"}
        score = analyzer._score_engagement(engagement)
        
        assert score == 85
