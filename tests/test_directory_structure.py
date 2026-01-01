"""
Tests for Task 1.1: Directory structure validation.

Purpose (Why):
Validates that all required directories exist for proper project organization.

Implementation (What):
Checks for existence of all required directories as specified in Task 1.1.
"""

import pytest
from pathlib import Path


class TestDirectoryStructure:
    """Test suite for directory structure validation."""
    
    def test_required_directories_exist(self, project_root: Path):
        """
        Test that all required directories exist.
        
        Arrange: Define required directory paths
        Act: Check if directories exist
        Assert: All directories must exist
        """
        required_dirs = [
            "app",
            "app/agent",
            "app/tools",
            "app/database",
            "app/models",
            "app/prompts",
            "data"
        ]
        
        missing_dirs = []
        for dir_path in required_dirs:
            full_path = project_root / dir_path
            if not full_path.exists():
                missing_dirs.append(dir_path)
        
        assert len(missing_dirs) == 0, (
            f"Missing required directories: {', '.join(missing_dirs)}"
        )
    
    def test_app_directory_is_package(self, project_root: Path):
        """
        Test that app directory exists and is accessible.
        
        Arrange: Project root path
        Act: Check app directory
        Assert: App directory exists
        """
        app_dir = project_root / "app"
        assert app_dir.exists(), "app/ directory does not exist"
        assert app_dir.is_dir(), "app/ is not a directory"
    
    def test_data_directory_exists(self, project_root: Path):
        """
        Test that data directory exists.
        
        Arrange: Project root path
        Act: Check data directory
        Assert: Data directory exists
        """
        data_dir = project_root / "data"
        assert data_dir.exists(), "data/ directory does not exist"
        assert data_dir.is_dir(), "data/ is not a directory"

