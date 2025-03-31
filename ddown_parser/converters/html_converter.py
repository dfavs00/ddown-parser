from typing import Dict, List, Any, Optional, Union
from ..utils.html_utils import build_html_attributes
from .base_converter import BaseConverter
from ..elements import (
    HeadingElement,
    ParagraphElement,
    ListElement,
    ListItemElement,
    CodeBlockElement,
    BlockquoteElement,
    ImageElement,
    LinkElement,
    TableElement
)


class HtmlConverter(BaseConverter):
    """Converter for transforming Ddown elements to HTML.
    
    This class handles the conversion of parsed Ddown elements into HTML format.
    """
    
    def __init__(self) -> None:
        """Initialize a new HTML converter."""
        super().__init__()
        
        # Dom Mode theme CSS - dark mode with purple and yellow accents
        self.dom_mode_css = """
        body {
            background-color: #1a1a2e;
            color: #e6e6e6;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            margin: 0;
            padding: 20px;
        }
        
        h1, h2, h3, h4, h5, h6 {
            color: #bb86fc; /* Purple accent */
            font-weight: 600;
            margin-top: 1.5em;
            margin-bottom: 0.5em;
        }
        
        h1 {
            font-size: 2.2em;
            border-bottom: 2px solid #bb86fc;
            padding-bottom: 0.3em;
        }
        
        h2 {
            font-size: 1.8em;
        }
        
        h3 {
            font-size: 1.5em;
        }
        
        a {
            color: #ffb300; /* Yellow accent */
            text-decoration: none;
        }
        
        a:hover {
            text-decoration: underline;
            color: #ffd54f;
        }
        
        p {
            margin: 1em 0;
        }
        
        ul, ol {
            margin: 1em 0;
            padding-left: 2em;
        }
        
        li {
            margin: 0.5em 0;
        }
        
        ul li::marker {
            color: #ffb300; /* Yellow accent */
            content: "=> ";
        }
        
        blockquote {
            border-left: 4px solid #bb86fc; /* Purple accent */
            margin: 1em 0;
            padding: 0.5em 1em;
            background-color: #2d2d42;
        }
        
        code {
            font-family: 'Courier New', Courier, monospace;
            background-color: #2d2d42;
            padding: 0.2em 0.4em;
            border-radius: 3px;
            color: #ffb300; /* Yellow accent */
        }
        
        pre {
            background-color: #2d2d42;
            padding: 1em;
            border-radius: 5px;
            overflow-x: auto;
        }
        
        pre code {
            background-color: transparent;
            padding: 0;
        }
        
        img {
            max-width: 100%;
            border-radius: 5px;
            border: 2px solid #bb86fc; /* Purple accent */
        }
        
        table {
            border-collapse: collapse;
            width: 100%;
            margin: 1em 0;
        }
        
        th {
            background-color: #bb86fc; /* Purple accent */
            color: #1a1a2e;
            font-weight: bold;
            text-align: left;
            padding: 0.5em;
        }
        
        td {
            border: 1px solid #2d2d42;
            padding: 0.5em;
        }
        
        tr:nth-child(even) {
            background-color: #2d2d42;
        }
        
        /* Dom's signature style */
        .dom-signature {
            text-align: right;
            font-style: italic;
            color: #bb86fc;
            margin-top: 2em;
        }
        """
    
    def convert(self, document: Dict[str, Any]) -> str:
        """Convert a parsed Ddown document to HTML.
        
        Args:
            document: Parsed Ddown document structure
            
        Returns:
            HTML string representation of the document
        """
        html_parts = []
        
        # Add HTML doctype and opening tags
        html_parts.append('<!DOCTYPE html>')
        html_parts.append('<html>')
        html_parts.append('<head>')
        html_parts.append('<meta charset="UTF-8">')
        html_parts.append('<meta name="viewport" content="width=device-width, initial-scale=1.0">')
        html_parts.append('<title>Ddown Document</title>')
        
        # Add styles
        html_parts.append('<style>')
        
        # Add dom-mode CSS if enabled
        if document.get('dom_mode', False):
            html_parts.append(self.dom_mode_css)
        
        # Add global styles if present
        if document.get('global_style'):
            html_parts.append(document['global_style'])
            
        html_parts.append('</style>')
        
        html_parts.append('</head>')
        html_parts.append('<body>')
        
        # Convert each element to HTML
        for element in document.get('elements', []):
            html_parts.append(self._convert_element_to_html(element))
        
        # Add Dom's signature if dom-mode is enabled
        if document.get('dom_mode', False):
            html_parts.append('<div class="dom-signature">Created with Ddown - Dom\'s Markdown</div>')
        
        # Add closing tags
        html_parts.append('</body>')
        html_parts.append('</html>')
        
        return '\n'.join(html_parts)
    
    def _convert_element_to_html(self, element: Dict[str, Any]) -> str:
        """Convert a single Ddown element to HTML.
        
        Args:
            element: Dictionary representation of a Ddown element
            
        Returns:
            HTML string representation of the element
        """
        element_type = element.get('type')
        content = element.get('content', '')
        attributes = element.get('attributes', {})
        
        if element_type == 'heading':
            return self._convert_heading(element)
        elif element_type == 'paragraph':
            return self._convert_paragraph(element)
        elif element_type == 'list':
            return self._convert_list(element)
        elif element_type == 'code_block':
            return self._convert_code_block(element)
        elif element_type == 'blockquote':
            return self._convert_blockquote(element)
        elif element_type == 'image':
            return self._convert_image(element)
        elif element_type == 'link':
            return self._convert_link(element)
        elif element_type == 'table':
            return self._convert_table(element)
        else:
            # Unknown element type
            return f'<!-- Unknown element type: {element_type} -->'
    
    def _convert_heading(self, element: Dict[str, Any]) -> str:
        """Convert a heading element to HTML.
        
        Args:
            element: Dictionary representation of a heading element
            
        Returns:
            HTML string representation of the heading
        """
        level = element.get('level', 1)
        content = element.get('content', '')
        attributes = element.get('attributes', {})
        
        attributes_str = build_html_attributes(attributes)
        return f"<h{level}{attributes_str}>{content}</h{level}>"
    
    def _convert_paragraph(self, element: Dict[str, Any]) -> str:
        """Convert a paragraph element to HTML.
        
        Args:
            element: Dictionary representation of a paragraph element
            
        Returns:
            HTML string representation of the paragraph
        """
        content = element.get('content', '')
        attributes = element.get('attributes', {})
        
        attributes_str = build_html_attributes(attributes)
        return f"<p{attributes_str}>{content}</p>"
    
    def _convert_list(self, element: Dict[str, Any]) -> str:
        """Convert a list element to HTML.
        
        Args:
            element: Dictionary representation of a list element
            
        Returns:
            HTML string representation of the list
        """
        list_type = element.get('list_type', 'unordered')
        items = element.get('items', [])
        attributes = element.get('attributes', {})
        
        attributes_str = build_html_attributes(attributes)
        
        if list_type == 'ordered':
            html = [f"<ol{attributes_str}>"]
        else:
            html = [f"<ul{attributes_str}>"]
        
        for item in items:
            html.append(self._convert_list_item(item))
        
        if list_type == 'ordered':
            html.append("</ol>")
        else:
            html.append("</ul>")
        
        return '\n'.join(html)
    
    def _convert_list_item(self, element: Dict[str, Any]) -> str:
        """Convert a list item element to HTML.
        
        Args:
            element: Dictionary representation of a list item element
            
        Returns:
            HTML string representation of the list item
        """
        content = element.get('content', '')
        attributes = element.get('attributes', {})
        
        attributes_str = build_html_attributes(attributes)
        return f"<li{attributes_str}>{content}</li>"
    
    def _convert_code_block(self, element: Dict[str, Any]) -> str:
        """Convert a code block element to HTML.
        
        Args:
            element: Dictionary representation of a code block element
            
        Returns:
            HTML string representation of the code block
        """
        content = element.get('content', '')
        language = element.get('language', '')
        attributes = element.get('attributes', {})
        
        # Add language class if specified
        if language:
            if 'classes' not in attributes:
                attributes['classes'] = []
            attributes['classes'].append(f"language-{language}")
        
        attributes_str = build_html_attributes(attributes)
        
        html = [f"<pre{attributes_str}>"]  # Pre tag for formatting
        html.append(f"<code>{content}</code>")
        html.append("</pre>")
        
        return '\n'.join(html)
    
    def _convert_blockquote(self, element: Dict[str, Any]) -> str:
        """Convert a blockquote element to HTML.
        
        Args:
            element: Dictionary representation of a blockquote element
            
        Returns:
            HTML string representation of the blockquote
        """
        content = element.get('content', '')
        attributes = element.get('attributes', {})
        
        attributes_str = build_html_attributes(attributes)
        return f"<blockquote{attributes_str}>{content}</blockquote>"
    
    def _convert_image(self, element: Dict[str, Any]) -> str:
        """Convert an image element to HTML.
        
        Args:
            element: Dictionary representation of an image element
            
        Returns:
            HTML string representation of the image
        """
        src = element.get('src', '')
        alt = element.get('alt', '')
        attributes = element.get('attributes', {})
        
        # Add src and alt to attributes
        attributes['src'] = src
        attributes['alt'] = alt
        
        attributes_str = build_html_attributes(attributes)
        return f"<img{attributes_str}>"
    
    def _convert_link(self, element: Dict[str, Any]) -> str:
        """Convert a link element to HTML.
        
        Args:
            element: Dictionary representation of a link element
            
        Returns:
            HTML string representation of the link
        """
        href = element.get('href', '')
        content = element.get('content', '')
        attributes = element.get('attributes', {})
        
        # Add href to attributes
        attributes['href'] = href
        
        attributes_str = build_html_attributes(attributes)
        return f"<a{attributes_str}>{content}</a>"
    
    def _convert_table(self, element: Dict[str, Any]) -> str:
        """Convert a table element to HTML.
        
        Args:
            element: Dictionary representation of a table element
            
        Returns:
            HTML string representation of the table
        """
        rows = element.get('rows', [])
        attributes = element.get('attributes', {})
        
        if not rows:
            return ""  # Skip empty tables
        
        attributes_str = build_html_attributes(attributes)
        html = [f"<table{attributes_str}>"]
        
        # First row is the header
        header_row = rows[0] if rows else []
        if header_row:
            html.append("<thead>")
            html.append("<tr>")
            for cell in header_row:
                html.append(f"<th>{cell}</th>")
            html.append("</tr>")
            html.append("</thead>")
        
        # Data rows
        if len(rows) > 1:
            html.append("<tbody>")
            for row in rows[1:]:  # Skip header row
                html.append("<tr>")
                for cell in row:
                    html.append(f"<td>{cell}</td>")
                html.append("</tr>")
            html.append("</tbody>")
        
        html.append("</table>")
        return "\n".join(html)
