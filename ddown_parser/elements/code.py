from typing import Dict, List, Any, Optional
from .base import DdownElement


class CodeBlockElement(DdownElement):
    """Represents a code block element in the Ddown document."""
    
    def __init__(self, content: str, language: Optional[str] = None,
                 attributes: Optional[Dict[str, Any]] = None) -> None:
        """Initialize a new code block element.
        
        Args:
            content: Content of the code block
            language: Programming language for syntax highlighting
            attributes: Additional attributes for the code block
        """
        super().__init__('code_block', content, attributes)
        self.language: Optional[str] = language
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the code block element to a dictionary representation.
        
        Returns:
            Dictionary representation of the code block element
        """
        result = super().to_dict()
        result['language'] = self.language
        return result
    
    def to_html(self) -> str:
        """Convert the code block element to HTML.
        
        Returns:
            HTML representation of the code block element
        """
        attributes_str = self._build_html_attributes()
        
        # Add language class if specified
        language_class = f" class=\"language-{self.language}\"" if self.language else ""
        
        # Escape HTML entities in code content
        content = self.content.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        
        return f"<pre{attributes_str}><code{language_class}>{content}</code></pre>"
    
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


class BlockquoteElement(DdownElement):
    """Represents a blockquote element in the Ddown document."""
    
    def __init__(self, content: str, attributes: Optional[Dict[str, Any]] = None) -> None:
        """Initialize a new blockquote element.
        
        Args:
            content: Content of the blockquote
            attributes: Additional attributes for the blockquote
        """
        super().__init__('blockquote', content, attributes)
    
    def to_html(self) -> str:
        """Convert the blockquote element to HTML.
        
        Returns:
            HTML representation of the blockquote element
        """
        attributes_str = self._build_html_attributes()
        return f"<blockquote{attributes_str}>{self.content}</blockquote>"
    
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
