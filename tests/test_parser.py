import unittest
from pathlib import Path
from typing import Dict, Any

from ddown_parser import DdownParser
from ddown_parser.elements import HeadingElement, ParagraphElement, ListItemElement


class TestDdownParser(unittest.TestCase):
    """Test cases for the Ddown parser."""
    
    def setUp(self) -> None:
        """Set up test fixtures."""
        self.parser = DdownParser()
        self.example_path = Path(__file__).parent.parent / "examples" / "simple.ddown"
    
    def test_parser_initialization(self) -> None:
        """Test that the parser initializes correctly."""
        self.assertIsNotNone(self.parser)
        self.assertIsInstance(self.parser.heading_patterns, dict)
        self.assertIsInstance(self.parser.list_patterns, dict)
        self.assertIsInstance(self.parser.style_patterns, dict)
    
    def test_extract_global_style(self) -> None:
        """Test extraction of global style from content."""
        content = """{@global-style}
h1 { color: red; }
{@endglobal-style}
Some content"""
        global_style = self.parser._extract_global_style(content)
        self.assertIsNotNone(global_style)
        self.assertIn("h1 { color: red; }", global_style)
    
    def test_parse_file_existence_check(self) -> None:
        """Test that parse_file raises FileNotFoundError for non-existent files."""
        with self.assertRaises(FileNotFoundError):
            self.parser.parse_file("non_existent_file.ddown")
    
    def test_parse_file_format_check(self) -> None:
        """Test that parse_file raises ValueError for unsupported formats."""
        # Create a temporary file for testing
        temp_file = Path("temp_test.ddown")
        temp_file.write_text("Test content")
        
        try:
            with self.assertRaises(ValueError):
                self.parser.parse_file(temp_file, output_format="unsupported")
        finally:
            # Clean up the temporary file
            if temp_file.exists():
                temp_file.unlink()
    
    def test_example_file_parsing(self) -> None:
        """Test parsing of the example file.
        
        This test will be expanded as the parser implementation progresses.
        """
        if self.example_path.exists():
            # For now, just check that parsing doesn't raise exceptions
            try:
                result = self.parser.parse_file(self.example_path)
                self.assertIsInstance(result, str)  # HTML output should be a string
            except Exception as e:
                self.fail(f"Parsing example file raised an exception: {e}")


if __name__ == "__main__":
    unittest.main()
