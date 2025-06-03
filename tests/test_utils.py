"""
Unit tests for utility functions.
"""

import pytest
import tempfile
import os
from pathlib import Path

from src.k1ngb0b_recon.utils import (
    validate_domain, sanitize_filename, create_directory_structure,
    deduplicate_subdomains, read_file_lines, write_file_lines
)


class TestUtils:
    """Test cases for utility functions."""
    
    def test_validate_domain(self):
        """Test domain validation."""
        # Valid domains
        assert validate_domain("example.com") == True
        assert validate_domain("sub.example.com") == True
        assert validate_domain("test-domain.co.uk") == True
        
        # Invalid domains
        assert validate_domain("") == False
        assert validate_domain("invalid") == False
        assert validate_domain("..com") == False
        
        # URLs should be handled
        assert validate_domain("https://example.com") == True
        assert validate_domain("http://sub.example.com") == True
    
    def test_sanitize_filename(self):
        """Test filename sanitization."""
        assert sanitize_filename("example.com") == "example_com"
        assert sanitize_filename("sub.example.com") == "sub_example_com"
        assert sanitize_filename("test-domain.co.uk") == "test-domain_co_uk"
        assert sanitize_filename("invalid/filename") == "invalid_filename"
    
    def test_create_directory_structure(self):
        """Test directory structure creation."""
        with tempfile.TemporaryDirectory() as temp_dir:
            dirs = create_directory_structure(temp_dir, "example.com")
            
            # Check that all directories are created
            for dir_path in dirs.values():
                assert Path(dir_path).exists()
                assert Path(dir_path).is_dir()
            
            # Check directory names
            assert "example_com" in dirs['base']
            assert "raw" in dirs['raw']
            assert "processed" in dirs['processed']
            assert "reports" in dirs['reports']
            assert "logs" in dirs['logs']
    
    def test_deduplicate_subdomains(self):
        """Test subdomain deduplication."""
        subdomains = [
            "example.com",
            "sub.example.com",
            "EXAMPLE.COM",  # Should be deduplicated
            "https://test.example.com",  # Should remove protocol
            "another.example.com:80",  # Should remove port
            "",  # Should be filtered out
            "invalid",  # Should be filtered out
            "sub.example.com"  # Duplicate
        ]
        
        result = deduplicate_subdomains(subdomains)
        
        # Check that duplicates are removed and domains are cleaned
        assert len(result) == 3  # example.com, sub.example.com, test.example.com, another.example.com
        assert "example.com" in result
        assert "sub.example.com" in result
        assert "test.example.com" in result
        assert "another.example.com" in result
        
        # Check that invalid entries are filtered
        assert "invalid" not in result
        assert "" not in result
    
    def test_file_operations(self):
        """Test file read/write operations."""
        with tempfile.TemporaryDirectory() as temp_dir:
            test_file = Path(temp_dir) / "test.txt"
            test_lines = ["line1", "line2", "line3"]
            
            # Test writing
            write_file_lines(str(test_file), test_lines)
            assert test_file.exists()
            
            # Test reading
            read_lines = read_file_lines(str(test_file))
            assert read_lines == test_lines
            
            # Test reading non-existent file
            non_existent = Path(temp_dir) / "non_existent.txt"
            assert read_file_lines(str(non_existent)) == []


if __name__ == "__main__":
    pytest.main([__file__])
