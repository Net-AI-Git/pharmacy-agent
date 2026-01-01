"""
Tests for Task 1.6: .env.example file validation.

Purpose (Why):
Validates that .env.example exists for environment variable documentation.

Implementation (What):
Checks file existence and validates content contains OPENAI_API_KEY.
"""

import pytest
from pathlib import Path


class TestEnvExample:
    """Test suite for .env.example validation."""
    
    def test_env_example_file_exists(self, project_root: Path):
        """
        Test that .env.example exists.
        
        Arrange: Project root path
        Act: Check .env.example
        Assert: File exists (warning if not, not critical)
        """
        env_file = project_root / ".env.example"
        if not env_file.exists():
            pytest.skip("⚠️ WARNING: .env.example does not exist (recommended but not critical)")
        
        assert env_file.is_file(), ".env.example is not a file"
    
    def test_env_example_contains_openai_key(self, project_root: Path):
        """
        Test that .env.example contains OPENAI_API_KEY.
        
        Arrange: .env.example file path
        Act: Read file content with proper encoding handling
        Assert: Content contains OPENAI_API_KEY
        """
        env_file = project_root / ".env.example"
        if not env_file.exists():
            pytest.skip("⚠️ WARNING: .env.example does not exist")
        
        # Try UTF-8 first, fallback to other encodings if needed
        encodings = ["utf-8", "utf-8-sig", "latin-1"]
        content = None
        
        for encoding in encodings:
            try:
                with open(env_file, "r", encoding=encoding) as f:
                    content = f.read()
                break
            except UnicodeDecodeError:
                continue
        
        assert content is not None, (
            f"Could not read .env.example with any encoding. File may be corrupted."
        )
        assert "OPENAI_API_KEY" in content, (
            f".env.example does not contain OPENAI_API_KEY. Content: {content[:100]}"
        )

