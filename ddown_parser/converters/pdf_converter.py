from typing import Dict, List, Any, Optional, Union, Tuple
import io
import os
import sys
import tempfile
import platform
from pathlib import Path
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
        
        # Try different PDF generation methods
        pdf_bytes = self._try_pdfkit(html_content)
        if pdf_bytes:
            return pdf_bytes
            
        pdf_bytes = self._try_weasyprint(html_content)
        if pdf_bytes:
            return pdf_bytes
            
        # If all methods fail, raise an error with detailed installation instructions
        system = platform.system()
        error_msg = "PDF conversion requires additional dependencies.\n\n"
        
        if system == "Windows":
            error_msg += "For Windows users:\n"
            error_msg += "1. Install pdfkit: pip install pdfkit\n"
            error_msg += "2. Download and install wkhtmltopdf from: https://wkhtmltopdf.org/downloads.html\n"
            error_msg += "3. Add the wkhtmltopdf bin directory to your PATH\n\n"
            error_msg += "Alternatively, you can use WeasyPrint:\n"
            error_msg += "1. Install GTK for Windows from: https://github.com/tschoonj/GTK-for-Windows-Runtime-Environment-Installer/releases\n"
            error_msg += "2. Install WeasyPrint: pip install weasyprint\n"
        elif system == "Darwin":  # macOS
            error_msg += "For macOS users:\n"
            error_msg += "1. Install pdfkit and wkhtmltopdf: brew install wkhtmltopdf && pip install pdfkit\n\n"
            error_msg += "Alternatively, you can use WeasyPrint:\n"
            error_msg += "1. Install dependencies: brew install cairo pango gdk-pixbuf libffi\n"
            error_msg += "2. Install WeasyPrint: pip install weasyprint\n"
        else:  # Linux
            error_msg += "For Linux users:\n"
            error_msg += "1. Install pdfkit and wkhtmltopdf: sudo apt-get install wkhtmltopdf && pip install pdfkit\n\n"
            error_msg += "Alternatively, you can use WeasyPrint:\n"
            error_msg += "1. Install dependencies: sudo apt-get install build-essential python3-dev python3-pip python3-setuptools python3-wheel python3-cffi libcairo2 libpango-1.0-0 libpangocairo-1.0-0 libgdk-pixbuf2.0-0 libffi-dev shared-mime-info\n"
            error_msg += "2. Install WeasyPrint: pip install weasyprint\n"
        
        raise ImportError(error_msg)
    
    def _try_weasyprint(self, html_content: str) -> Optional[bytes]:
        """Try to convert HTML to PDF using WeasyPrint.
        
        Args:
            html_content: HTML content to convert
            
        Returns:
            PDF bytes or None if WeasyPrint is not available
        """
        try:
            from weasyprint import HTML, CSS
            from weasyprint.text.fonts import FontConfiguration
            
            # Configure fonts
            font_config = FontConfiguration()
            
            # Convert HTML to PDF with proper styling
            pdf_bytes = HTML(string=html_content).write_pdf(
                stylesheets=[
                    CSS(string='@page { margin: 1cm; }')
                ],
                font_config=font_config
            )
            return pdf_bytes
        except ImportError:
            return None
        except Exception as e:
            print(f"WeasyPrint error: {e}", file=sys.stderr)
            return None
    
    def _try_pdfkit(self, html_content: str) -> Optional[bytes]:
        """Try to convert HTML to PDF using pdfkit.
        
        Args:
            html_content: HTML content to convert
            
        Returns:
            PDF bytes or None if pdfkit is not available
        """
        try:
            import pdfkit
            
            # Configure pdfkit options
            options = {
                'page-size': 'A4',
                'margin-top': '1cm',
                'margin-right': '1cm',
                'margin-bottom': '1cm',
                'margin-left': '1cm',
                'encoding': 'UTF-8',
                'quiet': ''
            }
            
            # Create a temporary HTML file
            with tempfile.NamedTemporaryFile(suffix='.html', delete=False, mode='w', encoding='utf-8') as f:
                f.write(html_content)
                temp_html_path = f.name
            
            try:
                # Convert HTML to PDF
                pdf_bytes = pdfkit.from_file(temp_html_path, False, options=options)
                return pdf_bytes
            finally:
                # Clean up the temporary file
                if os.path.exists(temp_html_path):
                    os.remove(temp_html_path)
                    
        except ImportError:
            return None
        except Exception as e:
            print(f"pdfkit error: {e}", file=sys.stderr)
            return None
