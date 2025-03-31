from typing import Dict, List, Any, Optional, Union
from pathlib import Path
import re
from .base_parser import BaseParser
from .element_parser import ElementParser


class DdownParser(BaseParser):
    """Main parser class for converting Ddown files to various output formats.
    
    This class handles parsing Ddown syntax into an intermediate representation
    and then converting that representation to the requested output format.
    """
    
    def __init__(self) -> None:
        """Initialize a new Ddown parser."""
        super().__init__()
        self.element_parser = ElementParser()
        self.output_formats: List[str] = ['html', 'pdf']
    
    def parse_file(self, file_path: Union[str, Path], output_format: str = 'html') -> Union[str, bytes]:
        """Parse a Ddown file and convert it to the specified output format.
        
        Args:
            file_path: Path to the Ddown file to parse
            output_format: Output format (html, pdf, etc.)
            
        Returns:
            Parsed content in the requested format (string for HTML, bytes for PDF)
            
        Raises:
            ValueError: If the output format is not supported
            FileNotFoundError: If the input file doesn't exist
        """
        # Validate output format
        if output_format not in self.output_formats:
            raise ValueError(f"Unsupported output format: {output_format}. Supported formats: {', '.join(self.output_formats)}")
        
        # Read the input file
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"Input file not found: {file_path}")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Parse the content
        document = self._parse_content(content)
        
        # Convert to the requested output format
        if output_format == 'html':
            return self._convert_to_html(document)
        elif output_format == 'pdf':
            return self._convert_to_pdf(document)
        
        # This should never happen due to the validation above
        raise ValueError(f"Unsupported output format: {output_format}")
    
    def _parse_content(self, content: str) -> Dict[str, Any]:
        """Parse Ddown content into an intermediate representation.
        
        Args:
            content: Raw Ddown content as a string
            
        Returns:
            A dictionary representing the parsed document structure
        """
        return {
            'global_style': self._extract_global_style(content),
            'elements': self._parse_elements(content),
        }
    
    def _extract_global_style(self, content: str) -> Optional[str]:
        """Extract global style definitions from the content.
        
        Args:
            content: Raw Ddown content
            
        Returns:
            CSS style string or None if no global style is defined
        """
        match = self.style_patterns['global'].search(content)
        if match:
            return match.group(1).strip()
        return None
    
    def _parse_elements(self, content: str) -> List[Dict[str, Any]]:
        """Parse all elements from the Ddown content.
        
        This method coordinates the parsing of different element types and
        ensures they are returned in the correct order.
        
        Args:
            content: Raw Ddown content
            
        Returns:
            List of parsed elements with their attributes
        """
        # Remove global style section if present to avoid parsing it as content
        content = self.style_patterns['global'].sub('', content)
        
        # Split content into lines for line-by-line processing
        lines = content.split('\n')
        processed_lines = [False] * len(lines)
        
        # Parse all elements with their positions in the document
        elements_with_position = []
        
        # Parse each type of element
        self.element_parser.parse_headings(content, lines, processed_lines, elements_with_position)
        self.element_parser.parse_code_blocks(content, lines, processed_lines, elements_with_position)
        self.element_parser.parse_blockquotes(lines, processed_lines, elements_with_position)
        self.element_parser.parse_tables(content, lines, processed_lines, elements_with_position)
        self.element_parser.parse_unordered_lists(lines, processed_lines, elements_with_position)
        self.element_parser.parse_ordered_lists(lines, processed_lines, elements_with_position)
        self.element_parser.parse_paragraphs(lines, processed_lines, elements_with_position)
        
        # Sort elements by their original position in the document
        elements_with_position.sort(key=lambda x: x['position'])
        
        # Extract just the elements
        elements = [item['element'] for item in elements_with_position]
        
        return elements
