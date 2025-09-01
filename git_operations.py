"""
Git operations module - handles all Git commands and operations
"""

import subprocess
import os
import json
from typing import List, Dict, Optional, Tuple
import threading
from datetime import datetime

class GitOperations:
    def __init__(self, repo_path: str = None):
        self.repo_path = repo_path or os.getcwd()
        
    def execute_command(self, command: List[str], cwd: str = None) -> Tuple[bool, str]:
        """Execute a Git command and return success status and output"""
        try:
            cwd = cwd or self.repo_path
            result = subprocess.run(
                command, 
                cwd=cwd, 
                capture_output=True, 
                text=True, 
                timeout=30
            )
            return result.returncode == 0, result.stdout + result.stderr
        except subprocess.TimeoutExpired:
            return False, "Command timed out"
        except Exception as e:
            return False, str(e)
    
    def is_git_repo(self, path: str = None) -> bool:
        """Check if the current directory is a Git repository"""
        path = path or self.repo_path
        success, _ = self.execute_command(['git', 'rev-parse', '--git-dir'], cwd=path)
        return success
    
    def init_repo(self, path: str) -> Tuple[bool, str]:
        """Initialize a new Git repository"""
        return self.execute_command(['git', 'init'], cwd=path)
    
    def clone_repo(self, url: str, path: str) -> Tuple[bool, str]:
        """Clone a repository"""
        return self.execute_command(['git', 'clone', url, path])
    
    def get_status(self) -> Dict:
        """Get repository status"""
        success, output = self.execute_command(['git', 'status', '--porcelain'])
        if not success:
            return {'error': output}
        
        modified = []
        staged = []
        untracked = []
        
        for line in output.strip().split('\n'):
            if not line:
                continue
            status = line[:2]
            filename = line[3:]
            
            if status[0] in ['M', 'A', 'D', 'R', 'C']:
                staged.append(filename)
            if status[1] in ['M', 'D']:
                modified.append(filename)
            elif status == '??':
                untracked.append(filename)
        
        return {
            'modified': modified,
            'staged': staged,
            'untracked': untracked
        }
    
    def add_files(self, files: List[str]) -> Tuple[bool, str]:
        """Stage files for commit"""
        return self.execute_command(['git', 'add'] + files)
    
    def commit(self, message: str) -> Tuple[bool, str]:
        """Commit staged changes"""
        return self.execute_command(['git', 'commit', '-m', message])
    
    def push(self, remote: str = 'origin', branch: str = None) -> Tuple[bool, str]:
        """Push changes to remote"""
        if branch:
            return self.execute_command(['git', 'push', remote, branch])
        return self.execute_command(['git', 'push'])
    
    def pull(self, remote: str = 'origin', branch: str = None) -> Tuple[bool, str]:
        """Pull changes from remote"""
        if branch:
            return self.execute_command(['git', 'pull', remote, branch])
        return self.execute_command(['git', 'pull'])
    
    def get_branches(self) -> List[str]:
        """Get list of branches"""
        success, output = self.execute_command(['git', 'branch'])
        if not success:
            return []
        
        branches = []
        for line in output.strip().split('\n'):
            if line:
                branch = line.strip().replace('* ', '')
                branches.append(branch)
        return branches
    
    def get_current_branch(self) -> str:
        """Get current branch name"""
        success, output = self.execute_command(['git', 'branch', '--show-current'])
        return output.strip() if success else 'unknown'
    
    def create_branch(self, name: str) -> Tuple[bool, str]:
        """Create a new branch"""
        return self.execute_command(['git', 'checkout', '-b', name])
    
    def switch_branch(self, name: str) -> Tuple[bool, str]:
        """Switch to a branch"""
        return self.execute_command(['git', 'checkout', name])
    
    def delete_branch(self, name: str, force: bool = False) -> Tuple[bool, str]:
        """Delete a branch"""
        flag = '-D' if force else '-d'
        return self.execute_command(['git', 'branch', flag, name])
    
    def merge_branch(self, branch: str) -> Tuple[bool, str]:
        """Merge a branch into current branch"""
        return self.execute_command(['git', 'merge', branch])
    
    def get_remotes(self) -> List[Dict[str, str]]:
        """Get list of remotes"""
        success, output = self.execute_command(['git', 'remote', '-v'])
        if not success:
            return []
        
        remotes = []
        for line in output.strip().split('\n'):
            if line:
                parts = line.split()
                if len(parts) >= 2:
                    remotes.append({
                        'name': parts[0],
                        'url': parts[1],
                        'type': parts[2] if len(parts) > 2 else ''
                    })
        return remotes
    
    def add_remote(self, name: str, url: str) -> Tuple[bool, str]:
        """Add a remote"""
        return self.execute_command(['git', 'remote', 'add', name, url])
    
    def remove_remote(self, name: str) -> Tuple[bool, str]:
        """Remove a remote"""
        return self.execute_command(['git', 'remote', 'remove', name])
    
    def get_commit_history(self, limit: int = 50) -> List[Dict]:
        """Get commit history"""
        success, output = self.execute_command([
            'git', 'log', '--oneline', '--graph', f'--max-count={limit}',
            '--pretty=format:%H|%an|%ae|%ad|%s', '--date=short'
        ])
        
        if not success:
            return []
        
        commits = []
        for line in output.strip().split('\n'):
            if '|' in line:
                # Extract graph part and commit info
                parts = line.split('|')
                if len(parts) >= 5:
                    commits.append({
                        'hash': parts[0].split()[-1],
                        'author': parts[1],
                        'email': parts[2],
                        'date': parts[3],
                        'message': parts[4],
                        'graph': line.split(parts[0])[0] if line.split(parts[0]) else ''
                    })
        return commits
    
    def get_file_diff(self, filename: str, staged: bool = False) -> str:
        """Get diff for a specific file"""
        cmd = ['git', 'diff']
        if staged:
            cmd.append('--cached')
        cmd.append(filename)
        
        success, output = self.execute_command(cmd)
        return output if success else f"Error getting diff: {output}"
    
    def set_config(self, key: str, value: str, global_config: bool = True) -> Tuple[bool, str]:
        """Set Git configuration"""
        cmd = ['git', 'config']
        if global_config:
            cmd.append('--global')
        cmd.extend([key, value])
        return self.execute_command(cmd)
    
    def get_config(self, key: str, global_config: bool = True) -> str:
        """Get Git configuration value"""
        cmd = ['git', 'config']
        if global_config:
            cmd.append('--global')
        cmd.append(key)
        
        success, output = self.execute_command(cmd)
        return output.strip() if success else ''