"""
Repository analyzer module for ghaly.

This module provides analysis functionality for GitHub repositories,
including activity metrics calculation and health scoring.
"""

from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional

from ghaly.github_api import GitHubClient


class HealthStatus(Enum):
    """Repository health status."""
    ACTIVE = "active"
    MODERATE = "moderate"
    INACTIVE = "inactive"


class RepositoryAnalyzer:
    """
    Analyzer for GitHub repository activity and health.
    
    Calculates various metrics including commit frequency,
    issue response time, contributor activity, and overall health score.
    """
    
    def __init__(self, github_client: GitHubClient, config: Optional[Dict[str, Any]] = None):
        """
        Initialize repository analyzer.
        
        Args:
            github_client: GitHub API client instance
            config: Configuration dictionary for thresholds and settings
        """
        self.client = github_client
        self.config = config or {}
        
        self.activity_days = self.config.get("activity_days", 30)
        self.thresholds = self.config.get("health_thresholds", {
            "active": 10,
            "moderate": 5
        })
    
    def analyze_repository(self, owner: str, repo: str) -> Dict[str, Any]:
        """
        Analyze a GitHub repository.
        
        Args:
            owner: Repository owner
            repo: Repository name
            
        Returns:
            Dictionary containing analysis results
        """
        stats = self.client.get_repository_stats(owner, repo, days=self.activity_days)
        
        metrics = self._calculate_metrics(stats)
        health = self._calculate_health(metrics)
        
        return {
            "repository": {
                "owner": owner,
                "name": repo,
                "full_name": f"{owner}/{repo}",
                "description": stats["repository"].get("description", ""),
                "language": stats["repository"].get("language", ""),
                "stars": stats["stargazers"],
                "forks": stats["forks"],
                "created_at": stats["created_at"],
                "updated_at": stats["updated_at"],
                "pushed_at": stats["pushed_at"]
            },
            "metrics": metrics,
            "health": health,
            "languages": stats["languages"],
            "contributors": stats["contributors"]["total"],
            "raw_stats": stats
        }
    
    def _calculate_metrics(self, stats: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate activity metrics from repository statistics.
        
        Args:
            stats: Repository statistics from GitHub API
            
        Returns:
            Dictionary containing calculated metrics
        """
        commits = stats["commits"]["recent"]
        issues = stats["issues"]["recent"]
        prs = stats["pull_requests"]["recent"]
        
        metrics = {
            "commit_frequency": self._calculate_commit_frequency(commits),
            "issue_activity": self._calculate_issue_activity(issues),
            "pr_activity": self._calculate_pr_activity(prs),
            "contributor_activity": self._calculate_contributor_activity(
                stats["contributors"]["recent"]
            ),
            "code_velocity": self._calculate_code_velocity(commits),
            "community_engagement": self._calculate_community_engagement(
                stats["stargazers"],
                stats["forks"],
                stats["issues"]["total"]
            )
        }
        
        return metrics
    
    def _calculate_commit_frequency(self, commits: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Calculate commit frequency metrics.
        
        Args:
            commits: List of commit data
            
        Returns:
            Dictionary with commit frequency metrics
        """
        total_commits = len(commits)
        
        if total_commits == 0:
            return {
                "total": 0,
                "per_day": 0.0,
                "per_week": 0.0,
                "per_month": 0.0
            }
        
        per_day = total_commits / self.activity_days
        per_week = per_day * 7
        per_month = per_day * 30
        
        return {
            "total": total_commits,
            "per_day": round(per_day, 2),
            "per_week": round(per_week, 2),
            "per_month": round(per_month, 2)
        }
    
    def _calculate_issue_activity(self, issues: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Calculate issue activity metrics.
        
        Args:
            issues: List of issue data
            
        Returns:
            Dictionary with issue activity metrics
        """
        total_issues = len(issues)
        open_issues = len([i for i in issues if i["state"] == "open"])
        closed_issues = len([i for i in issues if i["state"] == "closed"])
        
        avg_response_time = self._calculate_avg_response_time(issues)
        
        return {
            "total": total_issues,
            "open": open_issues,
            "closed": closed_issues,
            "close_rate": round(closed_issues / total_issues * 100, 1) if total_issues > 0 else 0,
            "avg_response_time_hours": avg_response_time
        }
    
    def _calculate_pr_activity(self, prs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Calculate pull request activity metrics.
        
        Args:
            prs: List of pull request data
            
        Returns:
            Dictionary with PR activity metrics
        """
        total_prs = len(prs)
        open_prs = len([p for p in prs if p["state"] == "open"])
        merged_prs = len([p for p in prs if p.get("merged_at")])
        
        return {
            "total": total_prs,
            "open": open_prs,
            "merged": merged_prs,
            "merge_rate": round(merged_prs / total_prs * 100, 1) if total_prs > 0 else 0
        }
    
    def _calculate_contributor_activity(self, contributors: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Calculate contributor activity metrics.
        
        Args:
            contributors: List of contributor data
            
        Returns:
            Dictionary with contributor activity metrics
        """
        total_contributors = len(contributors)
        
        if total_contributors == 0:
            return {
                "total": 0,
                "top_contributors": []
            }
        
        top_contributors = [
            {
                "login": c.get("login", "Unknown"),
                "contributions": c.get("contributions", 0)
            }
            for c in contributors[:5]
        ]
        
        return {
            "total": total_contributors,
            "top_contributors": top_contributors
        }
    
    def _calculate_code_velocity(self, commits: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Calculate code velocity metrics.
        
        Args:
            commits: List of commit data
            
        Returns:
            Dictionary with code velocity metrics
        """
        total_commits = len(commits)
        
        if total_commits == 0:
            return {
                "velocity": "low",
                "trend": "stable"
            }
        
        avg_commits_per_day = total_commits / self.activity_days
        
        if avg_commits_per_day >= 5:
            velocity = "high"
        elif avg_commits_per_day >= 2:
            velocity = "medium"
        else:
            velocity = "low"
        
        return {
            "velocity": velocity,
            "avg_commits_per_day": round(avg_commits_per_day, 2)
        }
    
    def _calculate_community_engagement(
        self,
        stars: int,
        forks: int,
        issues: int
    ) -> Dict[str, Any]:
        """
        Calculate community engagement metrics.
        
        Args:
            stars: Number of stargazers
            forks: Number of forks
            issues: Number of issues
            
        Returns:
            Dictionary with community engagement metrics
        """
        engagement_score = stars + (forks * 2) + (issues * 0.5)
        
        if engagement_score >= 1000:
            level = "very_high"
        elif engagement_score >= 500:
            level = "high"
        elif engagement_score >= 100:
            level = "moderate"
        elif engagement_score >= 50:
            level = "low"
        else:
            level = "very_low"
        
        return {
            "stars": stars,
            "forks": forks,
            "engagement_score": round(engagement_score, 1),
            "level": level
        }
    
    def _calculate_avg_response_time(self, issues: List[Dict[str, Any]]) -> Optional[float]:
        """
        Calculate average issue response time in hours.
        
        Args:
            issues: List of issue data
            
        Returns:
            Average response time in hours, or None if no closed issues
        """
        closed_issues = [i for i in issues if i["state"] == "closed"]
        
        if not closed_issues:
            return None
        
        response_times = []
        
        for issue in closed_issues:
            created_at = datetime.fromisoformat(issue["created_at"].replace('Z', '+00:00'))
            closed_at = datetime.fromisoformat(issue["closed_at"].replace('Z', '+00:00'))
            
            response_time = (closed_at - created_at).total_seconds() / 3600
            response_times.append(response_time)
        
        if not response_times:
            return None
        
        avg_response_time = sum(response_times) / len(response_times)
        
        return round(avg_response_time, 2)
    
    def _calculate_health(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate overall repository health score.
        
        Args:
            metrics: Calculated metrics
            
        Returns:
            Dictionary with health score and status
        """
        commit_score = self._score_commits(metrics["commit_frequency"])
        issue_score = self._score_issues(metrics["issue_activity"])
        pr_score = self._score_prs(metrics["pr_activity"])
        contributor_score = self._score_contributors(metrics["contributor_activity"])
        engagement_score = self._score_engagement(metrics["community_engagement"])
        
        total_score = (
            commit_score * 0.3 +
            issue_score * 0.2 +
            pr_score * 0.2 +
            contributor_score * 0.15 +
            engagement_score * 0.15
        )
        
        total_score = round(total_score, 1)
        
        status = self._determine_health_status(total_score)
        
        return {
            "score": total_score,
            "status": status.value,
            "breakdown": {
                "commits": round(commit_score, 1),
                "issues": round(issue_score, 1),
                "pull_requests": round(pr_score, 1),
                "contributors": round(contributor_score, 1),
                "engagement": round(engagement_score, 1)
            }
        }
    
    def _score_commits(self, commit_freq: Dict[str, Any]) -> float:
        """Score commit frequency."""
        per_day = commit_freq["per_day"]
        
        if per_day >= 5:
            return 100
        elif per_day >= 2:
            return 80
        elif per_day >= 1:
            return 60
        elif per_day >= 0.5:
            return 40
        else:
            return 20
    
    def _score_issues(self, issue_activity: Dict[str, Any]) -> float:
        """Score issue activity."""
        total = issue_activity["total"]
        close_rate = issue_activity["close_rate"]
        
        if total == 0:
            return 50
        
        score = (close_rate / 100) * 70 + min(total / 10, 30)
        return min(score, 100)
    
    def _score_prs(self, pr_activity: Dict[str, Any]) -> float:
        """Score pull request activity."""
        total = pr_activity["total"]
        merge_rate = pr_activity["merge_rate"]
        
        if total == 0:
            return 50
        
        score = (merge_rate / 100) * 70 + min(total / 5, 30)
        return min(score, 100)
    
    def _score_contributors(self, contributor_activity: Dict[str, Any]) -> float:
        """Score contributor activity."""
        total = contributor_activity["total"]
        
        if total >= 10:
            return 100
        elif total >= 5:
            return 80
        elif total >= 3:
            return 60
        elif total >= 1:
            return 40
        else:
            return 20
    
    def _score_engagement(self, engagement: Dict[str, Any]) -> float:
        """Score community engagement."""
        level = engagement["level"]
        
        scores = {
            "very_high": 100,
            "high": 85,
            "moderate": 65,
            "low": 45,
            "very_low": 25
        }
        
        return scores.get(level, 50)
    
    def _determine_health_status(self, score: float) -> HealthStatus:
        """
        Determine health status from score.
        
        Args:
            score: Health score (0-100)
            
        Returns:
            HealthStatus enum value
        """
        if score >= 70:
            return HealthStatus.ACTIVE
        elif score >= 40:
            return HealthStatus.MODERATE
        else:
            return HealthStatus.INACTIVE
