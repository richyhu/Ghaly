"""
OAuth authentication module for ghaly.

This module handles GitHub OAuth authentication flow including
authorization URL generation, token exchange, and token management.
"""

import secrets
import time
from typing import Dict, Optional
from urllib.parse import urlencode

import requests
from authlib.integrations.requests_client import OAuth2Session

from ghaly.config import ConfigManager, ConfigError


class GitHubOAuth:
    """
    GitHub OAuth authentication handler.
    
    Manages the OAuth 2.0 flow for GitHub authentication,
    including authorization, token exchange, and token storage.
    """
    
    def __init__(self, config: Optional[ConfigManager] = None):
        """
        Initialize GitHub OAuth handler.
        
        Args:
            config: Configuration manager instance. If None, uses global instance.
        """
        self.config = config or ConfigManager()
        
        self.client_id, self.client_secret = self.config.get_github_client_credentials()
        self.redirect_uri = self.config.get('github.redirect_uri')
        self.oauth_base_url = self.config.get('github.oauth_base_url')
        self.api_base_url = self.config.get('github.api_base_url')
        
        self.state = None
        self.oauth_session: Optional[OAuth2Session] = None
    
    def create_oauth_session(self) -> OAuth2Session:
        """
        Create OAuth2 session for GitHub.
        
        Returns:
            OAuth2Session instance configured for GitHub
        """
        return OAuth2Session(
            client_id=self.client_id,
            redirect_uri=self.redirect_uri,
            scope=["repo", "read:org", "user:email"]
        )
    
    def get_authorization_url(self) -> str:
        """
        Generate GitHub OAuth authorization URL.
        
        Returns:
            Authorization URL for user to visit
        """
        self.state = secrets.token_urlsafe(16)
        
        params = {
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "scope": "repo read:org user:email",
            "state": self.state,
            "allow_signup": "true"
        }
        
        auth_url = f"{self.oauth_base_url}/authorize?{urlencode(params)}"
        return auth_url
    
    def exchange_code_for_token(self, code: str, state: Optional[str] = None) -> Dict[str, any]:
        """
        Exchange authorization code for access token.
        
        Args:
            code: Authorization code from callback
            state: State parameter for CSRF protection
            
        Returns:
            Dictionary containing token data
            
        Raises:
            AuthError: If token exchange fails or state doesn't match
        """
        if state and state != self.state:
            raise AuthError("State parameter mismatch. Possible CSRF attack.")
        
        token_url = f"{self.oauth_base_url}/access_token"
        
        data = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "code": code,
            "redirect_uri": self.redirect_uri
        }
        
        headers = {
            "Accept": "application/json"
        }
        
        try:
            response = requests.post(token_url, data=data, headers=headers)
            response.raise_for_status()
            
            token_data = response.json()
            
            if "error" in token_data:
                raise AuthError(f"Token exchange failed: {token_data.get('error_description', token_data.get('error'))}")
            
            if "access_token" not in token_data:
                raise AuthError("No access token received from GitHub")
            
            token_data["expires_at"] = int(time.time()) + token_data.get("expires_in", 3600)
            
            self.config.save_token("github", token_data)
            
            return token_data
            
        except requests.RequestException as e:
            raise AuthError(f"Failed to exchange code for token: {e}")
    
    def get_access_token(self) -> str:
        """
        Get stored access token.
        
        Returns:
            Access token string
            
        Raises:
            AuthError: If no valid token is found
        """
        token_data = self.config.get_token("github")
        
        if not token_data:
            raise AuthError("No GitHub access token found. Please authenticate first.")
        
        access_token = token_data.get("access_token")
        
        if not access_token:
            raise AuthError("Invalid token data. Please authenticate again.")
        
        return access_token
    
    def refresh_token(self) -> Dict[str, any]:
        """
        Refresh access token if possible.
        
        Note: GitHub OAuth tokens don't expire by default, so this method
        is mainly for future compatibility or if refresh tokens are implemented.
        
        Returns:
            Dictionary containing new token data
            
        Raises:
            AuthError: If token refresh fails
        """
        token_data = self.config.get_token("github")
        
        if not token_data:
            raise AuthError("No token to refresh. Please authenticate first.")
        
        if "refresh_token" not in token_data:
            raise AuthError("GitHub tokens don't expire and don't support refresh.")
        
        token_url = f"{self.oauth_base_url}/access_token"
        
        data = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "grant_type": "refresh_token",
            "refresh_token": token_data["refresh_token"]
        }
        
        headers = {
            "Accept": "application/json"
        }
        
        try:
            response = requests.post(token_url, data=data, headers=headers)
            response.raise_for_status()
            
            new_token_data = response.json()
            
            if "error" in new_token_data:
                raise AuthError(f"Token refresh failed: {new_token_data.get('error_description')}")
            
            new_token_data["expires_at"] = int(time.time()) + new_token_data.get("expires_in", 3600)
            
            self.config.save_token("github", new_token_data)
            
            return new_token_data
            
        except requests.RequestException as e:
            raise AuthError(f"Failed to refresh token: {e}")
    
    def revoke_token(self) -> None:
        """
        Revoke and remove stored access token.
        
        Raises:
            AuthError: If token revocation fails
        """
        try:
            access_token = self.get_access_token()
            
            revoke_url = f"{self.oauth_base_url}/access_token"
            
            data = {
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "access_token": access_token
            }
            
            response = requests.delete(revoke_url, data=data)
            
            self.config.remove_token("github")
            
        except AuthError:
            raise
        except requests.RequestException as e:
            raise AuthError(f"Failed to revoke token: {e}")
    
    def get_authenticated_user(self) -> Dict[str, any]:
        """
        Get authenticated user information from GitHub.
        
        Returns:
            Dictionary containing user information
            
        Raises:
            AuthError: If request fails
        """
        access_token = self.get_access_token()
        
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/vnd.github.v3+json"
        }
        
        try:
            response = requests.get(f"{self.api_base_url}/user", headers=headers)
            response.raise_for_status()
            
            return response.json()
            
        except requests.RequestException as e:
            raise AuthError(f"Failed to get user information: {e}")
    
    def verify_token(self) -> bool:
        """
        Verify if the stored token is valid.
        
        Returns:
            True if token is valid, False otherwise
        """
        try:
            self.get_authenticated_user()
            return True
        except AuthError:
            return False
    
    def is_authenticated(self) -> bool:
        """
        Check if user is authenticated with valid token.
        
        Returns:
            True if authenticated, False otherwise
        """
        token_data = self.config.get_token("github")
        return token_data is not None and "access_token" in token_data


class AuthError(Exception):
    """Exception raised for authentication-related errors."""
    pass


def get_github_oauth() -> GitHubOAuth:
    """
    Get GitHub OAuth handler instance.
    
    Returns:
        GitHubOAuth instance
    """
    return GitHubOAuth()
