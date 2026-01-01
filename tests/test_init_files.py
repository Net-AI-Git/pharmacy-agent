"""
Tests for Task 1.2: __init__.py files validation.

Purpose (Why):
Validates that all Python packages have __init__.py files for proper module structure.

Implementation (What):
Checks for existence of __init__.py in all Python package directories.
"""

import pytest
from pathlib import Path


class TestInitFiles:
    """Test suite for __init__.py files validation."""
    
    def test_all_init_files_exist(self, project_root: Path):
        """
        Test that all required __init__.py files exist.
        
        Arrange: Define required __init__.py file paths
        Act: Check if files exist
        Assert: All __init__.py files must exist
        """
        required_init_files = [
            "app/__init__.py",
            "app/agent/__init__.py",
            "app/tools/__init__.py",
            "app/database/__init__.py",
            "app/models/__init__.py",
            "app/prompts/__init__.py"
        ]
        
        missing_files = []
        for file_path in required_init_files:
            full_path = project_root / file_path
            if not full_path.exists():
                missing_files.append(file_path)
        
        assert len(missing_files) == 0, (
            f"Missing required __init__.py files: {', '.join(missing_files)}"
        )
    
    def test_app_init_file_exists(self, project_root: Path):
        """
        Test that app/__init__.py exists.
        
        Arrange: Project root path
        Act: Check app/__init__.py
        Assert: File exists
        """
        init_file = project_root / "app" / "__init__.py"
        assert init_file.exists(), "app/__init__.py does not exist"
        assert init_file.is_file(), "app/__init__.py is not a file"

