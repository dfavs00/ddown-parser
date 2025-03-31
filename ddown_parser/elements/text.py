from typing import Dict, List, Any, Optional
from .base import DdownElement


class HeadingElement(DdownElement):
    """Represents a heading element in the Ddown document."""
    
    def __init__(self, content: str, level: int, 
                 attributes: Optional[Dict[str, Any]] = None) -> None:
        """Initialize a new heading element.
        
        Args:
            content: Content of the heading
            level: Heading level (1-5)
            attributes: Additional attributes for the heading
        """
        super().__init__('heading', content, attributes)
        self.level: int = level
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the heading element to a dictionary representation.
        
        Returns:
            Dictionary representation of the heading element
        """
        result = super().to_dict()
        result['level'] = self.level
        return result
    
    def to_html(self) -> str:
        """Convert the heading element to HTML.
        
        Returns:
            HTML representation of the heading element
        """
        attributes_str = self._build_html_attributes()
        return f"<h{self.level}{attributes_str}>{self.content}</h{self.level}>"
    
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


class ParagraphElement(DdownElement):
    """Represents a paragraph element in the Ddown document."""
    
    def __init__(self, content: str, attributes: Optional[Dict[str, Any]] = None) -> None:
        """Initialize a new paragraph element.
        
        Args:
            content: Content of the paragraph
            attributes: Additional attributes for the paragraph
        """
        super().__init__('paragraph', content, attributes)
    
    def to_html(self) -> str:
        """Convert the paragraph element to HTML.
        
        Returns:
            HTML representation of the paragraph element
        """
        attributes_str = self._build_html_attributes()
        return f"<p{attributes_str}>{self.content}</p>"
    
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
