from typing import Dict, List, Any, Optional
from .base import DdownElement


class ListItemElement(DdownElement):
    """Represents a list item element in the Ddown document."""
    
    def __init__(self, content: str, list_type: str = 'unordered', 
                 list_index: Optional[int] = None,
                 first_in_list: bool = False, last_in_list: bool = False,
                 list_attributes: Optional[Dict[str, Any]] = None,
                 attributes: Optional[Dict[str, Any]] = None) -> None:
        """Initialize a new list item element.
        
        Args:
            content: Content of the list item
            list_type: Type of the list ('ordered' or 'unordered')
            list_index: Index of the item in an ordered list
            first_in_list: Whether this is the first item in the list
            last_in_list: Whether this is the last item in the list
            list_attributes: Attributes for the parent list element
            attributes: Additional attributes for the list item
        """
        super().__init__('list_item', content, attributes)
        self.list_type: str = list_type
        self.list_index: Optional[int] = list_index
        self.first_in_list: bool = first_in_list
        self.last_in_list: bool = last_in_list
        self.list_attributes: Dict[str, Any] = list_attributes or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the list item element to a dictionary representation.
        
        Returns:
            Dictionary representation of the list item element
        """
        result = super().to_dict()
        result.update({
            'list_type': self.list_type,
            'list_index': self.list_index,
            'first_in_list': self.first_in_list,
            'last_in_list': self.last_in_list,
            'list_attributes': self.list_attributes
        })
        return result
    
    def to_html(self) -> str:
        """Convert the list item element to HTML.
        
        Returns:
            HTML representation of the list item element
        """
        attributes_str = self._build_html_attributes()
        return f"<li{attributes_str}>{self.content}</li>"
    
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


class ListElement(DdownElement):
    """Represents a list element in the Ddown document."""
    
    def __init__(self, items: List[Dict[str, Any]], list_type: str = 'unordered',
                 attributes: Optional[Dict[str, Any]] = None) -> None:
        """Initialize a new list element.
        
        Args:
            items: List of list items
            list_type: Type of the list ('ordered' or 'unordered')
            attributes: Additional attributes for the list
        """
        super().__init__('list', '', attributes)
        self.items: List[Dict[str, Any]] = items
        self.list_type: str = list_type
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the list element to a dictionary representation.
        
        Returns:
            Dictionary representation of the list element
        """
        result = super().to_dict()
        result.update({
            'list_type': self.list_type,
            'items': self.items
        })
        return result
    
    def to_html(self) -> str:
        """Convert the list element to HTML.
        
        Returns:
            HTML representation of the list element
        """
        attributes_str = self._build_html_attributes()
        tag = 'ol' if self.list_type == 'ordered' else 'ul'
        
        html = [f"<{tag}{attributes_str}>"]
        for item in self.items:
            if isinstance(item, dict):
                content = item.get('content', '')
                item_attributes = self._build_item_attributes(item.get('attributes', {}))
                html.append(f"<li{item_attributes}>{content}</li>")
            else:
                html.append(f"<li>{item}</li>")
        html.append(f"</{tag}>")
        
        return '\n'.join(html)
    
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
    
    def _build_item_attributes(self, attributes: Dict[str, Any]) -> str:
        """Build HTML attribute string for a list item.
        
        Args:
            attributes: Dictionary of attributes
            
        Returns:
            String of HTML attributes
        """
        if not attributes:
            return ""
        
        attr_parts = []
        
        # Handle style attributes
        if 'style' in attributes and attributes['style']:
            style_items = []
            for key, value in attributes['style'].items():
                style_items.append(f"{key}: {value}")
            if style_items:
                attr_parts.append(f"style=\"{'; '.join(style_items)}\"")
        
        # Handle class attributes
        if 'classes' in attributes and attributes['classes']:
            classes = ' '.join(attributes['classes'])
            attr_parts.append(f"class=\"{classes}\"")
        
        # Handle ID attribute
        if 'id' in attributes and attributes['id']:
            attr_parts.append(f"id=\"{attributes['id']}\"")
        
        # Handle other attributes
        for key, value in attributes.items():
            if key not in ['style', 'classes', 'id']:
                attr_parts.append(f"{key}=\"{value}\"")
        
        # Return attributes string with leading space if not empty
        return f" {' '.join(attr_parts)}" if attr_parts else ""
