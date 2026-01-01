"""
Tests for Task 1.4: requirements.txt validation.

Purpose (Why):
Validates that requirements.txt exists and contains correct dependencies
without forbidden packages.

Implementation (What):
Checks file existence, reads content, validates required packages,
and ensures no LangChain.
"""

import pytest
from pathlib import Path


class TestRequirements:
    """Test suite for requirements.txt validation."""
    
    def test_requirements_file_exists(self, project_root: Path):
        """
        Test that requirements.txt exists.
        
        Arrange: Project root path
        Act: Check requirements.txt
        Assert: File exists
        """
        req_file = project_root / "requirements.txt"
        assert req_file.exists(), "requirements.txt does not exist"
        assert req_file.is_file(), "requirements.txt is not a file"
    
    def test_required_packages_present(self, project_root: Path):
        """
        Test that all required packages are in requirements.txt.
        
        Arrange: Read requirements.txt content
        Act: Parse package names
        Assert: All required packages are present
        """
        req_file = project_root / "requirements.txt"
        with open(req_file, "r", encoding="utf-8") as f:
            content = f.read()
            lines = [line.strip() for line in content.split("\n") if line.strip()]
        
        found_packages = []
        for line in lines:
            package_name = line.split(">=")[0].split("==")[0].split("~=")[0].strip().lower()
            found_packages.append(package_name)
        
        required_packages = ["gradio", "openai", "pydantic", "python-dotenv"]
        missing_packages = [pkg for pkg in required_packages if pkg not in found_packages]
        
        assert len(missing_packages) == 0, (
            f"Missing required packages in requirements.txt: {', '.join(missing_packages)}"
        )
    
    def test_no_forbidden_packages(self, project_root: Path):
        """
        Test that no forbidden packages (LangChain) are present.
        
        Arrange: Read requirements.txt content
        Act: Parse package names
        Assert: No forbidden packages found
        """
        req_file = project_root / "requirements.txt"
        with open(req_file, "r", encoding="utf-8") as f:
            content = f.read()
            lines = [line.strip() for line in content.split("\n") if line.strip()]
        
        forbidden_packages = ["langchain", "langchain-"]
        forbidden_found = []
        
        for line in lines:
            package_name = line.split(">=")[0].split("==")[0].split("~=")[0].strip().lower()
            for forbidden in forbidden_packages:
                if forbidden in package_name:
                    forbidden_found.append(package_name)
        
        assert len(forbidden_found) == 0, (
            f"Forbidden packages found in requirements.txt: {', '.join(forbidden_found)}"
        )

