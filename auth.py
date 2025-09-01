"""
Authentication and credential management for Git Bridge
"""

import keyring
import json
import os
from typing import Optional, Dict
from utils import get_app_data_dir, ensure_dir_exists

class AuthManager:
    """Manages authentication and credential storage"""
    
    SERVICE_NAME = "GitBridge"
    
    def __init__(self):
        self.app_data_dir = get_app_data_dir()
        ensure_dir_exists(self.app_data_dir)
        self.config_file = os.path.join(self.app_data_dir, 'config.json')
        self.config = self._load_config()
    
    def _load_config(self) -> Dict:
        """Load configuration from file"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    return json.load(f)
        except Exception:
            pass
        return {}
    
    def _save_config(self):
        """Save configuration to file"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
        except Exception:
            pass
    
    def store_git_credentials(self, username: str, email: str, token: str = None):
        """Store Git credentials"""
        self.config['git_username'] = username
        self.config['git_email'] = email
        
        if token:
            try:
                keyring.set_password(self.SERVICE_NAME, username, token)
            except Exception:
                # Fallback to config file (less secure)
                self.config['git_token'] = token
        
        self._save_config()
    
    def get_git_credentials(self) -> Dict[str, str]:
        """Get stored Git credentials"""
        credentials = {
            'username': self.config.get('git_username', ''),
            'email': self.config.get('git_email', ''),
            'token': ''
        }
        
        username = credentials['username']
        if username:
            try:
                token = keyring.get_password(self.SERVICE_NAME, username)
                if token:
                    credentials['token'] = token
                else:
                    # Fallback to config file
                    credentials['token'] = self.config.get('git_token', '')
            except Exception:
                credentials['token'] = self.config.get('git_token', '')
        
        return credentials
    
    def clear_credentials(self):
        """Clear stored credentials"""
        username = self.config.get('git_username')
        if username:
            try:
                keyring.delete_password(self.SERVICE_NAME, username)
            except Exception:
                pass
        
        # Clear from config
        self.config.pop('git_username', None)
        self.config.pop('git_email', None)
        self.config.pop('git_token', None)
        self._save_config()
    
    def is_configured(self) -> bool:
        """Check if Git credentials are configured"""
        credentials = self.get_git_credentials()
        return bool(credentials['username'] and credentials['email'])
    
    def get_setting(self, key: str, default=None):
        """Get application setting"""
        return self.config.get(key, default)
    
    def set_setting(self, key: str, value):
        """Set application setting"""
        self.config[key] = value
        self._save_config()
    
    def get_recent_repos(self) -> list:
        """Get list of recent repositories"""
        return self.config.get('recent_repos', [])
    
    def add_recent_repo(self, repo_path: str):
        """Add repository to recent list"""
        recent = self.get_recent_repos()
        
        # Remove if already exists
        if repo_path in recent:
            recent.remove(repo_path)
        
        # Add to beginning
        recent.insert(0, repo_path)
        
        # Keep only last 10
        recent = recent[:10]
        
        self.set_setting('recent_repos', recent)
    
    def remove_recent_repo(self, repo_path: str):
        """Remove repository from recent list"""
        recent = self.get_recent_repos()
        if repo_path in recent:
            recent.remove(repo_path)
            self.set_setting('recent_repos', recent)