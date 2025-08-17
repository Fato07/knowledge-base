#!/usr/bin/env python3
"""
Test project detection functionality
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from capture.project_detector import ProjectDetector
import json

def test_project_detection():
    """Test project detection on various directories"""
    
    detector = ProjectDetector()
    
    print("🔍 Testing Project Detection")
    print("=" * 60)
    
    # Test paths
    test_paths = [
        Path.cwd(),  # Current directory
        Path.home() / "DEV" / "knowledge-base",
        Path.home() / "DEV" / "knowledge-base" / ".kb-daemon",
    ]
    
    for path in test_paths:
        if path.exists():
            print(f"\n📁 Path: {path}")
            print("-" * 40)
            
            project = detector.detect_project(path)
            
            print(f"Name: {project['name']}")
            print(f"Type: {project['type']}")
            print(f"Root: {project['path']}")
            if project.get('git_remote'):
                print(f"Git:  {project['git_remote']}")
            print(f"IDs:  {project.get('identifiers', {})}")
    
    print("\n" + "=" * 60)
    print("✅ Project detection test complete!")

if __name__ == "__main__":
    test_project_detection()
