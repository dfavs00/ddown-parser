from typing import Dict, List, Any, Optional
from .base import DdownElement


class ImageElement(DdownElement):
    """Represents an image element in the Ddown document."""
    
    def __init__(self, alt: str, src: str, attributes: Optional[Dict[str, Any]] = None) -> None:
        """Initialize a new image element.
        
        Args:
            alt: Alternative text for the image
            src: Source URL of the image
            attributes: Additional attributes for the image
        """
        super().__init__('image', '', attributes)
        self.alt: str = alt
        self.src: str = src
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the image element to a dictionary representation.
        
        Returns:
            Dictionary representation of the image element
        """
        result = super().to_dict()
        result['alt'] = self.alt
        result['src'] = self.src
        return result
    
    def to_html(self) -> str:
        """Convert the image element to HTML.
        
        Returns:
            HTML representation of the image element
        """
        attributes_str = self._build_html_attributes()
        return f"<img src=\"{self.src}\" alt=\"{self.alt}\"{attributes_str}>"
    
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


class LinkElement(DdownElement):
    """Represents a link element in the Ddown document."""
    
    def __init__(self, content: str, href: str, attributes: Optional[Dict[str, Any]] = None) -> None:
        """Initialize a new link element.
        
        Args:
            content: Text content of the link
            href: URL the link points to
            attributes: Additional attributes for the link
        """
        super().__init__('link', content, attributes)
        self.href: str = href
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the link element to a dictionary representation.
        
        Returns:
            Dictionary representation of the link element
        """
        result = super().to_dict()
        result['href'] = self.href
        return result
    
    def to_html(self) -> str:
        """Convert the link element to HTML.
        
        Returns:
            HTML representation of the link element
        """
        attributes_str = self._build_html_attributes()
        return f"<a href=\"{self.href}\"{attributes_str}>{self.content}</a>"
    
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
