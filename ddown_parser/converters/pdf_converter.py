from typing import Dict, List, Any, Optional, Union
import io
from .base_converter import BaseConverter
from .html_converter import HtmlConverter


class PdfConverter(BaseConverter):
    """Converter for transforming Ddown elements to PDF.
    
    This class handles the conversion of parsed Ddown elements into PDF format.
    It first converts to HTML and then uses a PDF library to generate the PDF.
    """
    
    def __init__(self) -> None:
        """Initialize a new PDF converter."""
        super().__init__()
        self.html_converter = HtmlConverter()
    
    def convert(self, document: Dict[str, Any]) -> bytes:
        """Convert a parsed Ddown document to PDF.
        
        Args:
            document: Parsed Ddown document structure
            
        Returns:
            PDF bytes
        """
        # First convert to HTML
        html_content = self.html_converter.convert(document)
        
        try:
            # Try to import weasyprint for PDF generation
            from weasyprint import HTML
            
            # Convert HTML to PDF
            pdf_bytes = HTML(string=html_content).write_pdf()
            return pdf_bytes
        except ImportError:
            # If weasyprint is not available, try pdfkit
            try:
                import pdfkit
                
                # Convert HTML to PDF
                pdf_bytes = pdfkit.from_string(html_content, False)
                return pdf_bytes
            except ImportError:
                # If neither library is available, raise an error
                raise ImportError(
                    "PDF conversion requires either 'weasyprint' or 'pdfkit' to be installed. "
                    "Please install one of these packages using pip."
                )
