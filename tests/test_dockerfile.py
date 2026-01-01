"""
Tests for Task 1.7: Dockerfile validation.

Purpose (Why):
Validates that Dockerfile exists and has correct structure for containerization.

Implementation (What):
Checks file existence and validates key components (Python 3.11, requirements.txt, CMD).
"""

import pytest
from pathlib import Path


class TestDockerfile:
    """Test suite for Dockerfile validation."""
    
    def test_dockerfile_exists(self, project_root: Path):
        """
        Test that Dockerfile exists.
        
        Arrange: Project root path
        Act: Check Dockerfile
        Assert: File exists
        """
        dockerfile = project_root / "Dockerfile"
        assert dockerfile.exists(), "Dockerfile does not exist"
        assert dockerfile.is_file(), "Dockerfile is not a file"
    
    def test_dockerfile_contains_python311(self, project_root: Path):
        """
        Test that Dockerfile uses Python 3.11.
        
        Arrange: Read Dockerfile content
        Act: Check for python:3.11
        Assert: Contains Python 3.11
        """
        dockerfile = project_root / "Dockerfile"
        with open(dockerfile, "r", encoding="utf-8") as f:
            content = f.read()
        
        assert "python:3.11" in content, (
            "Dockerfile does not use Python 3.11"
        )
    
    def test_dockerfile_contains_requirements(self, project_root: Path):
        """
        Test that Dockerfile references requirements.txt.
        
        Arrange: Read Dockerfile content
        Act: Check for requirements.txt
        Assert: Contains requirements.txt reference
        """
        dockerfile = project_root / "Dockerfile"
        with open(dockerfile, "r", encoding="utf-8") as f:
            content = f.read()
        
        assert "requirements.txt" in content, (
            "Dockerfile does not reference requirements.txt"
        )
    
    def test_dockerfile_contains_cmd(self, project_root: Path):
        """
        Test that Dockerfile has CMD instruction.
        
        Arrange: Read Dockerfile content
        Act: Check for CMD
        Assert: Contains CMD instruction
        """
        dockerfile = project_root / "Dockerfile"
        with open(dockerfile, "r", encoding="utf-8") as f:
            content = f.read()
        
        assert "CMD" in content, (
            "Dockerfile does not contain CMD instruction"
        )

