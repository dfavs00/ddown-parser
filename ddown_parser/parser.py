from typing import Dict, List, Optional, Union, Any
from pathlib import Path

# Import the refactored parser and converters
from .parsers.ddown_parser import DdownParser as RefactoredParser
from .converters.html_converter import HtmlConverter
from .converters.pdf_converter import PdfConverter


class DdownParser:
    """Main parser class for converting Ddown files to various output formats.
    
    This class serves as a compatibility wrapper around the refactored implementation.
    """
    
    def __init__(self) -> None:
        """Initialize a new Ddown parser."""
        self._parser = RefactoredParser()
        self._html_converter = HtmlConverter()
        self._pdf_converter = PdfConverter()
        self.output_formats = self._parser.output_formats
    
    def parse_file(self, file_path: Union[str, Path], output_format: str = 'html', custom_css: Optional[str] = None) -> Union[str, bytes]:
        """Parse a Ddown file and convert it to the specified output format.
        
        Args:
            file_path: Path to the Ddown file to parse
            output_format: Output format (html, pdf, etc.)
            custom_css: Optional custom CSS to apply to the output
            
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
        file_path = Path(file_path) if isinstance(file_path, str) else file_path
        if not file_path.exists():
            raise FileNotFoundError(f"Input file not found: {file_path}")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Parse the content
        document = self._parse_content(content)
        
        # Add custom CSS if provided
        if custom_css:
            if 'global_styles' not in document:
                document['global_styles'] = custom_css
            else:
                document['global_styles'] += "\n" + custom_css
        
        # Convert to the requested output format
        if output_format == 'html':
            return self._convert_to_html(document, custom_css)
        elif output_format == 'pdf':
            return self._convert_to_pdf(document, custom_css)
        
        # This should never happen due to the validation above
        raise ValueError(f"Unsupported output format: {output_format}")
    
    def _parse_content(self, content: str) -> Dict[str, Any]:
        """Parse Ddown content into an intermediate representation.
        
        Args:
            content: Raw Ddown content as a string
            
        Returns:
            A dictionary representing the parsed document structure
        """
        return self._parser._parse_content(content)
    
    def _convert_to_html(self, document: Dict[str, Any], custom_css: Optional[str] = None) -> str:
        """Convert a parsed document to HTML.
        
        Args:
            document: Parsed document structure
            custom_css: Optional custom CSS to apply to the output
            
        Returns:
            HTML string
        """
        if custom_css and 'global_styles' not in document:
            document['global_styles'] = custom_css
        elif custom_css:
            document['global_styles'] += "\n" + custom_css
            
        return self._html_converter.convert(document)
    
    def _convert_to_pdf(self, document: Dict[str, Any], custom_css: Optional[str] = None) -> bytes:
        """Convert a parsed document to PDF.
        
        Args:
            document: Parsed document structure
            custom_css: Optional custom CSS to apply to the output
            
        Returns:
            PDF bytes
        """
        if custom_css and 'global_styles' not in document:
            document['global_styles'] = custom_css
        elif custom_css:
            document['global_styles'] += "\n" + custom_css
            
        return self._pdf_converter.convert(document)
