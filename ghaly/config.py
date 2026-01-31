"""
Configuration management module for ghaly.

This module handles loading, saving, and managing configuration settings
including OAuth credentials, API keys, and user preferences.
"""

import json
import os
from pathlib import Path
from typing import Any, Dict, Optional

from dotenv import load_dotenv


class ConfigManager:
    """
    Manages configuration settings for ghaly.
    
    Handles loading from environment variables and JSON config files,
    with support for OAuth credentials, API keys, and user preferences.
    """
    
    def __init__(self, config_dir: Optional[Path] = None):
        """
        Initialize the configuration manager.
        
        Args:
            config_dir: Custom configuration directory. If None, uses project
                       directory .ghaly or ~/.ghaly as fallback.
        """
        if config_dir is None:
            current_dir = Path.cwd()
            project_config_dir = current_dir / ".ghaly"
            
            if project_config_dir.exists() or current_dir.name == "ghaly":
                self.config_dir = project_config_dir
            else:
                home_dir = Path.home()
                self.config_dir = home_dir / ".ghaly"
        else:
            self.config_dir = Path(config_dir)
        
        self.config_file = self.config_dir / "config.json"
        self.tokens_file = self.config_dir / "tokens.json"
        self.env_file = self.config_dir / ".env"
        
        self.config: Dict[str, Any] = {}
        self.tokens: Dict[str, Any] = {}
        
        self._ensure_config_dir()
        self._load_config()
        self._load_tokens()
        self._load_env()
        self._load_project_env()
    
    def _ensure_config_dir(self) -> None:
        """Create configuration directory if it doesn't exist."""
        self.config_dir.mkdir(parents=True, exist_ok=True)
    
    def _load_config(self) -> None:
        """Load configuration from JSON file."""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    self.config = json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                self.config = {}
        else:
            self.config = self._get_default_config()
            self._save_config()
    
    def _save_config(self) -> None:
        """Save configuration to JSON file."""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
        except IOError as e:
            raise ConfigError(f"Failed to save config: {e}")
    
    def _load_tokens(self) -> None:
        """Load OAuth tokens from JSON file."""
        if self.tokens_file.exists():
            try:
                with open(self.tokens_file, 'r', encoding='utf-8') as f:
                    self.tokens = json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                self.tokens = {}
        else:
            self.tokens = {}
    
    def _save_tokens(self) -> None:
        """Save OAuth tokens to JSON file."""
        try:
            with open(self.tokens_file, 'w', encoding='utf-8') as f:
                json.dump(self.tokens, f, indent=2, ensure_ascii=False)
            os.chmod(self.tokens_file, 0o600)
        except IOError as e:
            raise ConfigError(f"Failed to save tokens: {e}")
    
    def _load_env(self) -> None:
        """Load environment variables from .env file."""
        if self.env_file.exists():
            load_dotenv(self.env_file)
    
    def _load_project_env(self) -> None:
        """Load environment variables from project directory .env file."""
        try:
            current_dir = Path.cwd()
            project_env = current_dir / ".env"
            if project_env.exists() and project_env != self.env_file:
                load_dotenv(project_env)
        except Exception:
            pass
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration values."""
        return {
            "github": {
                "api_base_url": "https://api.github.com",
                "oauth_base_url": "https://github.com/login/oauth",
                "client_id": "",
                "client_secret": "",
                "redirect_uri": "http://localhost:8080/callback"
            },
            "openai": {
                "api_base_url": "https://api.openai.com/v1",
                "api_key": "",
                "model": "gpt-3.5-turbo"
            },
            "analysis": {
                "activity_days": 30,
                "health_thresholds": {
                    "active": 10,
                    "moderate": 5
                }
            },
            "output": {
                "format": "table",
                "color": True
            },
            "ui": {
                "language": "zh"
            }
        }
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value by key.
        
        Args:
            key: Configuration key (supports dot notation, e.g., 'github.client_id')
            default: Default value if key not found
            
        Returns:
            Configuration value or default
        """
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def set(self, key: str, value: Any) -> None:
        """
        Set configuration value by key.
        
        Args:
            key: Configuration key (supports dot notation, e.g., 'github.client_id')
            value: Value to set
        """
        keys = key.split('.')
        config = self.config
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        config[keys[-1]] = value
        self._save_config()
    
    def get_env(self, key: str, default: Any = None) -> Any:
        """
        Get environment variable value.
        
        Args:
            key: Environment variable name
            default: Default value if not found
            
        Returns:
            Environment variable value or default
        """
        return os.getenv(key, default)
    
    def save_token(self, token_type: str, token_data: Dict[str, Any]) -> None:
        """
        Save OAuth token data.
        
        Args:
            token_type: Type of token (e.g., 'github')
            token_data: Token data dictionary
        """
        self.tokens[token_type] = token_data
        self._save_tokens()
    
    def get_token(self, token_type: str) -> Optional[Dict[str, Any]]:
        """
        Get OAuth token data.
        
        Args:
            token_type: Type of token (e.g., 'github')
            
        Returns:
            Token data dictionary or None if not found
        """
        return self.tokens.get(token_type)
    
    def remove_token(self, token_type: str) -> None:
        """
        Remove OAuth token data.
        
        Args:
            token_type: Type of token (e.g., 'github')
        """
        if token_type in self.tokens:
            del self.tokens[token_type]
            self._save_tokens()
    
    def save_siliconflow_api_key(self, api_key: str) -> None:
        """
        Save SiliconFlow API key.
        
        Args:
            api_key: SiliconFlow API key
        """
        self.config['siliconflow.api_key'] = api_key
        self._save_config()
    
    def get_siliconflow_api_key(self) -> Optional[str]:
        """
        Get SiliconFlow API key.
        
        Returns:
            SiliconFlow API key or None if not found
        """
        return self.config.get('siliconflow.api_key') or self.get_env('OPENAI_API_KEY')
    
    def clear_all_tokens(self) -> None:
        """Clear all stored OAuth tokens."""
        self.tokens = {}
        self._save_tokens()
    
    def reset_config(self) -> None:
        """Reset configuration to default values."""
        self.config = self._get_default_config()
        self._save_config()
    
    def is_configured(self) -> bool:
        """
        Check if essential configuration is set.
        
        Returns:
            True if essential configuration is set, False otherwise
        """
        github_client_id = self.get('github.client_id')
        github_client_secret = self.get('github.client_secret')
        openai_api_key = self.get_env('OPENAI_API_KEY') or self.get('openai.api_key')
        
        return bool(github_client_id and github_client_secret and openai_api_key)
    
    def get_github_client_credentials(self) -> tuple[str, str]:
        """
        Get GitHub OAuth client credentials.
        
        Returns:
            Tuple of (client_id, client_secret)
            
        Raises:
            ConfigError: If credentials are not configured
        """
        client_id = self.get('github.client_id') or self.get_env('GITHUB_CLIENT_ID')
        client_secret = self.get('github.client_secret') or self.get_env('GITHUB_CLIENT_SECRET')
        
        if not client_id or not client_secret:
            raise ConfigError(
                "GitHub OAuth credentials not configured. "
                "Please set them using 'ghaly auth configure' or environment variables."
            )
        
        return client_id, client_secret
    
    def get_openai_api_key(self) -> str:
        """
        Get OpenAI API key.
        
        Returns:
            OpenAI API key
            
        Raises:
            ConfigError: If API key is not configured
        """
        api_key = self.get_env('OPENAI_API_KEY') or self.get('openai.api_key')
        
        if not api_key:
            raise ConfigError(
                "OpenAI API key not configured. "
                "Please set it using 'ghaly auth configure' or environment variable OPENAI_API_KEY."
            )
        
        return api_key
    
    def get_language(self) -> str:
        """
        Get UI language setting.
        
        Returns:
            Language code ('zh' or 'en')
        """
        return self.get('ui.language', 'zh')
    
    def set_language(self, language: str) -> None:
        """
        Set UI language.
        
        Args:
            language: Language code ('zh' or 'en')
        """
        if language not in ['zh', 'en']:
            raise ValueError("Language must be 'zh' or 'en'")
        self.set('ui.language', language)


class ConfigError(Exception):
    """Exception raised for configuration-related errors."""
    pass


_global_config: Optional[ConfigManager] = None


def get_config() -> ConfigManager:
    """
    Get the global configuration manager instance.
    
    Returns:
        Global ConfigManager instance
    """
    global _global_config
    if _global_config is None:
        _global_config = ConfigManager()
    return _global_config
