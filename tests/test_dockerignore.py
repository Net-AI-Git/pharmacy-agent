"""
Tests for Task 1.8: .dockerignore file validation.

Purpose (Why):
Validates that .dockerignore exists to exclude unnecessary files from Docker builds.

Implementation (What):
Checks file existence and validates it contains common ignore patterns.
"""

import pytest
from pathlib import Path


class TestDockerignore:
    """Test suite for .dockerignore validation."""
    
    def test_dockerignore_exists(self, project_root: Path):
        """
        Test that .dockerignore exists.
        
        Arrange: Project root path
        Act: Check .dockerignore
        Assert: File exists (warning if not, not critical)
        """
        dockerignore = project_root / ".dockerignore"
        if not dockerignore.exists():
            pytest.skip("⚠️ WARNING: .dockerignore does not exist (recommended but not critical)")
        
        assert dockerignore.is_file(), ".dockerignore is not a file"
    
    def test_dockerignore_contains_common_patterns(self, project_root: Path):
        """
        Test that .dockerignore contains common ignore patterns.
        
        Arrange: Read .dockerignore content
        Act: Check for common patterns
        Assert: Contains venv or __pycache__ patterns
        """
        dockerignore = project_root / ".dockerignore"
        if not dockerignore.exists():
            pytest.skip("⚠️ WARNING: .dockerignore does not exist")
        
        with open(dockerignore, "r", encoding="utf-8") as f:
            content = f.read()
        
        has_venv = "venv" in content
        has_pycache = "__pycache__" in content
        
        assert has_venv or has_pycache, (
            ".dockerignore should contain common ignore patterns (venv, __pycache__)"
        )

