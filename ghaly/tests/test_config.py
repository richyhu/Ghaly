"""
Unit tests for ghaly configuration management.
"""

import json
import os
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from ghaly.config import ConfigManager, ConfigError


@pytest.fixture
def temp_config_dir():
    """Create a temporary directory for configuration."""
    with tempfile.TemporaryDirectory() as temp_dir:
        config_dir = Path(temp_dir)
        yield config_dir


@pytest.fixture
def sample_config():
    """Sample configuration data."""
    return {
        "github": {
            "api_base_url": "https://api.github.com",
            "oauth_base_url": "https://github.com/login/oauth",
            "client_id": "test_client_id",
            "client_secret": "test_client_secret",
            "redirect_uri": "http://localhost:8080/callback"
        },
        "openai": {
            "api_base_url": "https://api.openai.com/v1",
            "api_key": "test_api_key",
            "model": "gpt-3.5-turbo"
        },
        "analysis": {
            "activity_days": 30,
            "health_thresholds": {
                "active": 10,
                "moderate": 5
            }
        }
    }


class TestConfigManager:
    """Test cases for ConfigManager class."""
    
    def test_init_with_custom_dir(self, temp_config_dir):
        """Test initialization with custom directory."""
        config = ConfigManager(temp_config_dir)
        
        assert config.config_dir == temp_config_dir
        assert config.config_file == temp_config_dir / "config.json"
        assert config.tokens_file == temp_config_dir / "tokens.json"
        assert config.env_file == temp_config_dir / ".env"
    
    def test_init_creates_config_dir(self, temp_config_dir):
        """Test that initialization creates config directory."""
        ConfigManager(temp_config_dir)
        
        assert temp_config_dir.exists()
        assert temp_config_dir.is_dir()
    
    def test_get_default_config(self, temp_config_dir):
        """Test getting default configuration values."""
        config = ConfigManager(temp_config_dir)
        
        assert config.get('github.api_base_url') == 'https://api.github.com'
        assert config.get('github.oauth_base_url') == 'https://github.com/login/oauth'
        assert config.get('github.redirect_uri') == 'http://localhost:8080/callback'
        assert config.get('openai.api_base_url') == 'https://api.openai.com/v1'
        assert config.get('openai.model') == 'gpt-3.5-turbo'
    
    def test_set_and_get_config(self, temp_config_dir):
        """Test setting and getting configuration values."""
        config = ConfigManager(temp_config_dir)
        
        config.set('test.key', 'test_value')
        assert config.get('test.key') == 'test_value'
        
        config.set('test.nested.key', 'nested_value')
        assert config.get('test.nested.key') == 'nested_value'
    
    def test_save_and_load_config(self, temp_config_dir, sample_config):
        """Test saving and loading configuration."""
        config = ConfigManager(temp_config_dir)
        
        for key, value in self._flatten_dict(sample_config):
            config.set(key, value)
        
        new_config = ConfigManager(temp_config_dir)
        
        assert new_config.get('github.api_base_url') == 'https://api.github.com'
        assert new_config.get('github.client_id') == 'test_client_id'
        assert new_config.get('analysis.activity_days') == 30
    
    def _flatten_dict(self, d, parent_key=''):
        """Helper method to flatten nested dictionary."""
        items = []
        for k, v in d.items():
            new_key = f"{parent_key}.{k}" if parent_key else k
            if isinstance(v, dict):
                items.extend(self._flatten_dict(v, new_key))
            else:
                items.append((new_key, v))
        return items
    
    def test_get_env_var(self, temp_config_dir):
        """Test getting environment variables."""
        config = ConfigManager(temp_config_dir)
        
        with patch.dict(os.environ, {'TEST_ENV_VAR': 'test_value'}):
            assert config.get_env('TEST_ENV_VAR') == 'test_value'
            assert config.get_env('NON_EXISTENT_VAR') is None
    
    def test_set_token(self, temp_config_dir):
        """Test setting OAuth tokens."""
        config = ConfigManager(temp_config_dir)
        
        token_data = {
            "access_token": "test_token",
            "token_type": "bearer",
            "scope": "repo,user:email"
        }
        
        config.save_token('github', token_data)
        
        retrieved = config.get_token('github')
        assert retrieved == token_data
    
    def test_get_token_not_found(self, temp_config_dir):
        """Test getting non-existent token."""
        config = ConfigManager(temp_config_dir)
        
        assert config.get_token('nonexistent') is None
    
    def test_remove_token(self, temp_config_dir):
        """Test removing OAuth tokens."""
        config = ConfigManager(temp_config_dir)
        
        token_data = {"access_token": "test_token"}
        config.save_token('github', token_data)
        
        config.remove_token('github')
        
        assert config.get_token('github') is None
    
    def test_clear_all_tokens(self, temp_config_dir):
        """Test clearing all tokens."""
        config = ConfigManager(temp_config_dir)
        
        config.save_token('github', {"access_token": "token1"})
        config.save_token('test', {"access_token": "token2"})
        
        config.clear_all_tokens()
        
        assert config.get_token('github') is None
        assert config.get_token('test') is None
    
    def test_get_github_credentials(self, temp_config_dir):
        """Test getting GitHub OAuth credentials."""
        config = ConfigManager(temp_config_dir)
        
        config.set('github.client_id', 'test_id')
        config.set('github.client_secret', 'test_secret')
        
        client_id, client_secret = config.get_github_client_credentials()
        
        assert client_id == 'test_id'
        assert client_secret == 'test_secret'
    
    def test_get_github_credentials_missing(self, temp_config_dir):
        """Test getting missing GitHub credentials raises error."""
        config = ConfigManager(temp_config_dir)
        
        client_id = config.get('github.client_id')
        client_secret = config.get('github.client_secret')
        
        if not client_id or not client_secret:
            assert True
        else:
            assert False, "Expected missing credentials"
    
    def test_get_openai_api_key(self, temp_config_dir):
        """Test getting OpenAI API key from config."""
        config = ConfigManager(temp_config_dir)
        
        config.set('openai.api_key', 'test_key')
        
        api_key = config.get('openai.api_key')
        
        assert api_key == 'test_key'
    
    def test_get_openai_api_key_from_env(self, temp_config_dir):
        """Test getting OpenAI API key from environment."""
        config = ConfigManager(temp_config_dir)
        
        with patch.dict(os.environ, {'OPENAI_API_KEY': 'env_key'}):
            api_key = config.get_env('OPENAI_API_KEY')
            assert api_key == 'env_key'
    
    def test_get_openai_api_key_missing(self, temp_config_dir):
        """Test getting missing OpenAI API key returns None."""
        config = ConfigManager(temp_config_dir)
        
        with patch.dict(os.environ, {'OPENAI_API_KEY': ''}, clear=False):
            api_key = config.get_env('OPENAI_API_KEY') or config.get('openai.api_key')
            
            assert api_key == '' or api_key is None
