from typing import Dict, List, Any, Optional, Union, Callable, Type
from abc import ABC, abstractmethod
from io import BytesIO


class BaseRenderer(ABC):
    """Abstract base class for all renderers.
    
    Renderers are responsible for converting the parsed Ddown document
    to specific output formats like HTML, PDF, etc.
    """
    
    @abstractmethod
    def render(self, document: Dict[str, Any]) -> Union[str, bytes]:
        """Render the document to the target format.
        
        Args:
            document: Parsed document structure
            
        Returns:
            Rendered content in the target format
        """
        pass


class HtmlRenderer(BaseRenderer):
    """Renderer for converting Ddown to HTML.
    
    This renderer converts the parsed Ddown document to HTML with
    appropriate CSS styling.
    """
    
    def __init__(self) -> None:
        # Element rendering functions mapped by element type
        self.element_renderers: Dict[str, Callable] = {
            'heading': self._render_heading,
            'paragraph': self._render_paragraph,
            'list_item': self._render_list_item,
            'code_block': self._render_code_block,
            'blockquote': self._render_blockquote,
            'image': self._render_image,
            'link': self._render_link,
            'table': self._render_table,
        }
    
    def render(self, document: Dict[str, Any]) -> str:
        """Render the document to HTML.
        
        Args:
            document: Parsed document structure
            
        Returns:
            HTML string representation of the document
        """
        # Start with HTML document structure
        html_parts: List[str] = [
            "<!DOCTYPE html>",
            "<html>",
            "<head>",
            "<meta charset=\"UTF-8\">",
            "<title>Ddown Document</title>"
        ]
        
        # Add global styles if present
        if document.get('global_style'):
            html_parts.append(f"<style>{document['global_style']}</style>")
        
        html_parts.append("</head>")
        html_parts.append("<body>")
        
        # Render each element in the document
        for element in document.get('elements', []):
            element_type = element.get('type')
            if element_type in self.element_renderers:
                html_parts.append(self.element_renderers[element_type](element))
            else:
                # Fallback for unknown element types
                html_parts.append(f"<!-- Unknown element type: {element_type} -->")
        
        html_parts.append("</body>")
        html_parts.append("</html>")
        
        return "\n".join(html_parts)
    
    def _render_heading(self, element: Dict[str, Any]) -> str:
        """Render a heading element to HTML.
        
        Args:
            element: Heading element data
            
        Returns:
            HTML string for the heading
        """
        level = element.get('level', 1)  # Default to h1 if level not specified
        content = element.get('content', '')
        attributes = self._build_html_attributes(element.get('attributes', {}))
        
        return f"<h{level}{attributes}>{content}</h{level}>"
    
    def _render_paragraph(self, element: Dict[str, Any]) -> str:
        """Render a paragraph element to HTML.
        
        Args:
            element: Paragraph element data
            
        Returns:
            HTML string for the paragraph
        """
        content = element.get('content', '')
        attributes = self._build_html_attributes(element.get('attributes', {}))
        
        return f"<p{attributes}>{content}</p>"
    
    def _render_list_item(self, element: Dict[str, Any]) -> str:
        """Render a list item element to HTML.
        
        This method handles both ordered and unordered list items.
        
        Args:
            element: List item element data
            
        Returns:
            HTML string for the list item
        """
        content = element.get('content', '')
        list_type = element.get('list_type', 'unordered')  # 'ordered' or 'unordered'
        attributes = self._build_html_attributes(element.get('attributes', {}))
        
        # Start a new list if this is the first item
        list_start = ''
        if element.get('first_in_list', False):
            list_tag = 'ol' if list_type == 'ordered' else 'ul'
            list_attributes = self._build_html_attributes(element.get('list_attributes', {}))
            list_start = f"<{list_tag}{list_attributes}>"
        
        # End the list if this is the last item
        list_end = ''
        if element.get('last_in_list', False):
            list_tag = 'ol' if list_type == 'ordered' else 'ul'
            list_end = f"</{list_tag}>"
        
        return f"{list_start}<li{attributes}>{content}</li>{list_end}"
    
    def _render_code_block(self, element: Dict[str, Any]) -> str:
        """Render a code block element to HTML.
        
        Args:
            element: Code block element data
            
        Returns:
            HTML string for the code block
        """
        content = element.get('content', '')
        language = element.get('language', '')
        attributes = self._build_html_attributes(element.get('attributes', {}))
        
        # Add language class if specified
        if language:
            class_attr = f" class=\"language-{language}\""
        else:
            class_attr = ""
        
        return f"<pre{attributes}><code{class_attr}>{content}</code></pre>"
    
    def _render_blockquote(self, element: Dict[str, Any]) -> str:
        """Render a blockquote element to HTML.
        
        Args:
            element: Blockquote element data
            
        Returns:
            HTML string for the blockquote
        """
        content = element.get('content', '')
        attributes = self._build_html_attributes(element.get('attributes', {}))
        
        return f"<blockquote{attributes}>{content}</blockquote>"
    
    def _render_image(self, element: Dict[str, Any]) -> str:
        """Render an image element to HTML.
        
        Args:
            element: Image element data
            
        Returns:
            HTML string for the image
        """
        src = element.get('src', '')
        alt = element.get('alt', '')
        attributes = self._build_html_attributes(element.get('attributes', {}))
        
        return f"<img src=\"{src}\" alt=\"{alt}\"{attributes}>"
    
    def _render_link(self, element: Dict[str, Any]) -> str:
        """Render a link element to HTML.
        
        Args:
            element: Link element data
            
        Returns:
            HTML string for the link
        """
        href = element.get('href', '')
        content = element.get('content', '')
        attributes = self._build_html_attributes(element.get('attributes', {}))
        
        return f"<a href=\"{href}\"{attributes}>{content}</a>"
    
    def _render_table(self, element: Dict[str, Any]) -> str:
        """Render a table element to HTML.
        
        Args:
            element: Table element data
            
        Returns:
            HTML string for the table
        """
        rows = element.get('rows', [])
        attributes = self._build_html_attributes(element.get('attributes', {}))
        
        html = [f"<table{attributes}>", "<thead>", "<tr>"]
        
        # Add header row
        header_row = rows[0] if rows else []
        for cell in header_row:
            html.append(f"<th>{cell}</th>")
        
        html.append("</tr>", "</thead>", "<tbody>")
        
        # Add data rows
        for row in rows[1:] if rows else []:
            html.append("<tr>")
            for cell in row:
                html.append(f"<td>{cell}</td>")
            html.append("</tr>")
        
        html.append("</tbody>", "</table>")
        
        return "\n".join(html)
    
    def _build_html_attributes(self, attributes: Dict[str, Any]) -> str:
        """Build HTML attribute string from attributes dictionary.
        
        Args:
            attributes: Dictionary of attributes
            
        Returns:
            String of HTML attributes (including leading space if not empty)
        """
        if not attributes:
            return ""
        
        attr_parts = []
        
        # Handle style attributes
        if 'style' in attributes:
            style_items = []
            for key, value in attributes['style'].items():
                style_items.append(f"{key}: {value}")
            if style_items:
                attr_parts.append(f"style=\"{'; '.join(style_items)}\"")
        
        # Handle class attributes
        if 'classes' in attributes and attributes['classes']:
            attr_parts.append(f"class=\"{' '.join(attributes['classes'])}\"")
        
        # Handle ID attribute
        if 'id' in attributes and attributes['id']:
            attr_parts.append(f"id=\"{attributes['id']}\"")
        
        # Handle other attributes
        for key, value in attributes.items():
            if key not in ['style', 'classes', 'id']:
                attr_parts.append(f"{key}=\"{value}\"")
        
        return f" {' '.join(attr_parts)}" if attr_parts else ""


class PdfRenderer(BaseRenderer):
    """Renderer for converting Ddown to PDF.
    
    This renderer first converts the document to HTML using the HtmlRenderer,
    then uses WeasyPrint to convert the HTML to PDF.
    """
    
    def __init__(self) -> None:
        self.html_renderer = HtmlRenderer()
    
    def render(self, document: Dict[str, Any]) -> bytes:
        """Render the document to PDF.
        
        Args:
            document: Parsed document structure
            
        Returns:
            PDF content as bytes
        """
        # First convert to HTML
        html = self.html_renderer.render(document)
        
        # Then convert HTML to PDF using WeasyPrint
        # This is a placeholder - in a real implementation, we would use WeasyPrint here
        # from weasyprint import HTML
        # pdf_bytes = HTML(string=html).write_pdf()
        # return pdf_bytes
        
        # For now, return empty bytes as a placeholder
        return b""  # Placeholder


class RendererFactory:
    """Factory for creating renderers based on the requested output format."""
    
    _renderers: Dict[str, Type[BaseRenderer]] = {
        'html': HtmlRenderer,
        'pdf': PdfRenderer,
    }
    
    @classmethod
    def get_renderer(cls, output_format: str) -> BaseRenderer:
        """Get a renderer for the specified output format.
        
        Args:
            output_format: The desired output format (html, pdf, etc.)
            
        Returns:
            An instance of the appropriate renderer
            
        Raises:
            ValueError: If the output format is not supported
        """
        if output_format not in cls._renderers:
            raise ValueError(f"Unsupported output format: {output_format}. "
                             f"Supported formats: {', '.join(cls._renderers.keys())}")
        
        return cls._renderers[output_format]()
