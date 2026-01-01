"""
Pytest configuration and shared fixtures.

Purpose (Why):
Provides common test fixtures and configuration for all tests,
ensuring consistency and reducing code duplication.

Implementation (What):
Defines pytest fixtures for common test data and utilities.
"""

import pytest
from pathlib import Path


@pytest.fixture
def project_root() -> Path:
    """
    Fixture providing the project root directory.
    
    Returns:
        Path to the project root directory
    """
    return Path(__file__).parent.parent


@pytest.fixture
def data_dir(project_root: Path) -> Path:
    """
    Fixture providing the data directory path.
    
    Args:
        project_root: Project root directory fixture
        
    Returns:
        Path to the data directory
    """
    return project_root / "data"


@pytest.fixture
def database_json_path(data_dir: Path) -> Path:
    """
    Fixture providing the database.json file path.
    
    Args:
        data_dir: Data directory fixture
        
    Returns:
        Path to database.json
    """
    return data_dir / "database.json"

