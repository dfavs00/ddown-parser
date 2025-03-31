from typing import Dict, List, Any, Optional
from .base import DdownElement


class TableElement(DdownElement):
    """Represents a table element in the Ddown document."""
    
    def __init__(self, rows: List[List[str]], attributes: Optional[Dict[str, Any]] = None) -> None:
        """Initialize a new table element.
        
        Args:
            rows: List of rows, where each row is a list of cell contents
            attributes: Additional attributes for the table
        """
        super().__init__('table', '', attributes)
        self.rows: List[List[str]] = rows
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the table element to a dictionary representation.
        
        Returns:
            Dictionary representation of the table element
        """
        result = super().to_dict()
        result['rows'] = self.rows
        return result
    
    def to_html(self) -> str:
        """Convert the table element to HTML.
        
        Returns:
            HTML representation of the table element
        """
        if not self.rows:
            return ""  # Skip empty tables
        
        attributes_str = self._build_html_attributes()
        html = [f"<table{attributes_str}>"]
        
        # First row is the header
        header_row = self.rows[0] if self.rows else []
        if header_row:
            html.append("<thead>")
            html.append("<tr>")
            for cell in header_row:
                html.append(f"<th>{cell}</th>")
            html.append("</tr>")
            html.append("</thead>")
        
        # Data rows
        if len(self.rows) > 1:
            html.append("<tbody>")
            for row in self.rows[1:]:  # Skip header row
                html.append("<tr>")
                for cell in row:
                    html.append(f"<td>{cell}</td>")
                html.append("</tr>")
            html.append("</tbody>")
        
        html.append("</table>")
        return "\n".join(html)
    
    def _build_html_attributes(self) -> str:
        """Build HTML attribute string from the element's attributes.
        
        Returns:
            String of HTML attributes
        """
        if not self.attributes:
            return ""
        
        attr_parts = []
        
        # Handle style attributes
        if 'style' in self.attributes and self.attributes['style']:
            style_items = []
            for key, value in self.attributes['style'].items():
                style_items.append(f"{key}: {value}")
            if style_items:
                attr_parts.append(f"style=\"{'; '.join(style_items)}\"")
        
        # Handle class attributes
        if 'classes' in self.attributes and self.attributes['classes']:
            classes = ' '.join(self.attributes['classes'])
            attr_parts.append(f"class=\"{classes}\"")
        
        # Handle ID attribute
        if 'id' in self.attributes and self.attributes['id']:
            attr_parts.append(f"id=\"{self.attributes['id']}\"")
        
        # Handle other attributes
        for key, value in self.attributes.items():
            if key not in ['style', 'classes', 'id']:
                attr_parts.append(f"{key}=\"{value}\"")
        
        # Return attributes string with leading space if not empty
        return f" {' '.join(attr_parts)}" if attr_parts else ""
