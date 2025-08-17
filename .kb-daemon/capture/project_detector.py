#!/usr/bin/env python3
"""
Project Detector - Automatically detect and track current project context
"""

import os
import json
import subprocess
from pathlib import Path
from typing import Dict, Optional, List
from datetime import datetime

class ProjectDetector:
    """Detect current project from various indicators"""
    
    def __init__(self, base_path: Path = None):
        self.base_path = base_path or Path.cwd()
        self.cache_file = Path.home() / ".kb-daemon" / "project_cache.json"
        self.project_cache = self._load_cache()
        
    def _load_cache(self) -> Dict:
        """Load project cache"""
        if self.cache_file.exists():
            try:
                with open(self.cache_file) as f:
                    return json.load(f)
            except:
                pass
        return {}
    
    def _save_cache(self):
        """Save project cache"""
        self.cache_file.parent.mkdir(exist_ok=True)
        with open(self.cache_file, 'w') as f:
            json.dump(self.project_cache, f, indent=2)
    
    def detect_project(self, path: Path = None) -> Dict:
        """
        Detect project from current directory
        Returns: {
            'name': 'project-name',
            'type': 'node|python|rust|go|unknown',
            'path': '/full/path',
            'git_remote': 'github.com/user/repo',
            'identifiers': {...}
        }
        """
        check_path = path or Path.cwd()
        
        # Check cache first
        cache_key = str(check_path.resolve())
        if cache_key in self.project_cache:
            cached = self.project_cache[cache_key]
            # Cache for 1 hour
            if (datetime.now().timestamp() - cached.get('timestamp', 0)) < 3600:
                return cached['project']
        
        project_info = {
            'name': check_path.name,
            'type': 'unknown',
            'path': str(check_path.resolve()),
            'git_remote': None,
            'identifiers': {}
        }
        
        # 1. Check Git repository
        git_info = self._detect_git(check_path)
        if git_info:
            project_info.update(git_info)
        
        # 2. Detect project type from files
        project_type = self._detect_project_type(check_path)
        project_info['type'] = project_type
        
        # 3. Get project name from package files
        project_name = self._get_project_name(check_path, project_type)
        if project_name:
            project_info['name'] = project_name
        
        # 4. Find project root (go up until no more project files)
        project_root = self._find_project_root(check_path)
        if project_root != check_path:
            project_info['path'] = str(project_root.resolve())
            project_info['name'] = project_root.name
        
        # Cache the result
        self.project_cache[cache_key] = {
            'project': project_info,
            'timestamp': datetime.now().timestamp()
        }
        self._save_cache()
        
        return project_info
    
    def _detect_git(self, path: Path) -> Optional[Dict]:
        """Detect git repository info"""
        try:
            # Check if it's a git repo
            result = subprocess.run(
                ['git', 'rev-parse', '--git-dir'],
                cwd=path,
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                return None
            
            # Get remote URL
            result = subprocess.run(
                ['git', 'config', '--get', 'remote.origin.url'],
                cwd=path,
                capture_output=True,
                text=True
            )
            
            remote_url = result.stdout.strip() if result.returncode == 0 else None
            
            # Parse GitHub/GitLab URL to get project name
            if remote_url:
                # Convert SSH to HTTPS format for consistency
                if remote_url.startswith('git@'):
                    remote_url = remote_url.replace(':', '/').replace('git@', 'https://')
                
                # Remove .git suffix
                remote_url = remote_url.removesuffix('.git')
                
                # Extract project name from URL
                parts = remote_url.split('/')
                if len(parts) >= 2:
                    project_name = parts[-1]
                    org_name = parts[-2]
                    
                    return {
                        'name': project_name,
                        'git_remote': remote_url,
                        'identifiers': {
                            'git_org': org_name,
                            'git_project': project_name
                        }
                    }
            
            # Get current branch
            result = subprocess.run(
                ['git', 'branch', '--show-current'],
                cwd=path,
                capture_output=True,
                text=True
            )
            
            branch = result.stdout.strip() if result.returncode == 0 else 'main'
            
            return {
                'git_remote': remote_url,
                'identifiers': {
                    'git_branch': branch
                }
            }
            
        except Exception:
            return None
    
    def _detect_project_type(self, path: Path) -> str:
        """Detect project type from characteristic files"""
        
        # Check for project files in priority order
        checks = [
            # Node.js/JavaScript
            (['package.json'], 'node'),
            (['yarn.lock'], 'node'),
            (['pnpm-lock.yaml'], 'node'),
            
            # Python
            (['requirements.txt'], 'python'),
            (['setup.py'], 'python'),
            (['pyproject.toml'], 'python'),
            (['Pipfile'], 'python'),
            (['poetry.lock'], 'python'),
            
            # Rust
            (['Cargo.toml'], 'rust'),
            
            # Go
            (['go.mod'], 'go'),
            
            # Ruby
            (['Gemfile'], 'ruby'),
            
            # Java
            (['pom.xml'], 'java'),
            (['build.gradle'], 'java'),
            
            # C/C++
            (['CMakeLists.txt'], 'cpp'),
            (['Makefile'], 'c'),
            
            # .NET
            (['.csproj', '.sln'], 'dotnet'),
            
            # Docker
            (['Dockerfile'], 'docker'),
            (['docker-compose.yml', 'docker-compose.yaml'], 'docker'),
        ]
        
        for files, project_type in checks:
            for file in files:
                if (path / file).exists() or list(path.glob(f'*{file}')):
                    return project_type
        
        return 'unknown'
    
    def _get_project_name(self, path: Path, project_type: str) -> Optional[str]:
        """Extract project name from package files"""
        
        try:
            if project_type == 'node':
                package_json = path / 'package.json'
                if package_json.exists():
                    with open(package_json) as f:
                        data = json.load(f)
                        return data.get('name', path.name)
            
            elif project_type == 'python':
                # Check setup.py
                setup_py = path / 'setup.py'
                if setup_py.exists():
                    # Simple regex to find name= in setup()
                    content = setup_py.read_text()
                    import re
                    match = re.search(r'name\s*=\s*["\']([^"\']+)["\']', content)
                    if match:
                        return match.group(1)
                
                # Check pyproject.toml
                pyproject = path / 'pyproject.toml'
                if pyproject.exists():
                    try:
                        import tomllib
                        with open(pyproject, 'rb') as f:
                            data = tomllib.load(f)
                            return data.get('project', {}).get('name', path.name)
                    except ImportError:
                        # Fallback for Python < 3.11
                        try:
                            import toml
                            data = toml.load(pyproject)
                            return data.get('project', {}).get('name', path.name)
                        except:
                            pass
            
            elif project_type == 'rust':
                cargo_toml = path / 'Cargo.toml'
                if cargo_toml.exists():
                    try:
                        import toml
                        data = toml.load(cargo_toml)
                        return data.get('package', {}).get('name', path.name)
                    except:
                        pass
            
            elif project_type == 'go':
                go_mod = path / 'go.mod'
                if go_mod.exists():
                    content = go_mod.read_text()
                    lines = content.split('\n')
                    if lines and lines[0].startswith('module '):
                        module_name = lines[0].replace('module ', '').strip()
                        return module_name.split('/')[-1]
        
        except Exception:
            pass
        
        return None
    
    def _find_project_root(self, path: Path) -> Path:
        """Find project root by going up until no more project files"""
        
        current = path.resolve()
        project_type = None
        
        # Keep going up while we find project indicators
        while current.parent != current:
            # Check if this looks like a project root
            if (current / '.git').exists():
                return current
            
            # Check for root-level project files
            root_indicators = [
                'package.json', 'requirements.txt', 'setup.py',
                'Cargo.toml', 'go.mod', 'Gemfile', 'pom.xml',
                '.gitignore', 'README.md', 'Makefile'
            ]
            
            has_indicator = any((current / f).exists() for f in root_indicators)
            
            if has_indicator:
                # Check if parent also has indicators
                parent = current.parent
                parent_has_indicator = any((parent / f).exists() for f in root_indicators)
                
                # If parent doesn't have indicators, we found the root
                if not parent_has_indicator or (parent / '.git').exists():
                    return current
            
            current = current.parent
            
            # Stop at home or root directory
            if current == Path.home() or current == Path('/'):
                break
        
        return path
    
    def track_project_switch(self, old_project: Dict, new_project: Dict) -> Dict:
        """Create an event for project context switch"""
        
        return {
            'type': 'project_switch',
            'timestamp': datetime.now().isoformat(),
            'data': {
                'from_project': old_project.get('name'),
                'to_project': new_project.get('name'),
                'from_path': old_project.get('path'),
                'to_path': new_project.get('path'),
                'duration_seconds': None  # Will be calculated later
            },
            'importance': 5,
            'category': 'context_switch'
        }


# Test function
def test_detector():
    """Test the project detector"""
    detector = ProjectDetector()
    
    # Test current directory
    project = detector.detect_project()
    print("Current Project:")
    print(json.dumps(project, indent=2))
    
    # Test some common paths
    test_paths = [
        Path.home() / "DEV" / "knowledge-base",
        Path.cwd()
    ]
    
    for path in test_paths:
        if path.exists():
            print(f"\n{path}:")
            project = detector.detect_project(path)
            print(json.dumps(project, indent=2))


if __name__ == "__main__":
    test_detector()
