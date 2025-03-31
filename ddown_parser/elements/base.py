from typing import Dict, List, Any, Optional, Tuple, Union


class DdownElement:
    """Base class for all Ddown elements.
    
    This class represents a parsed element in the Ddown document,
    such as a heading, paragraph, list item, etc.
    """
    
    def __init__(self, element_type: str, content: str, 
                 attributes: Optional[Dict[str, Any]] = None) -> None:
        """Initialize a new Ddown element.
        
        Args:
            element_type: Type of the element (heading, list_item, paragraph, etc.)
            content: Content of the element
            attributes: Additional attributes for the element (styles, classes, etc.)
        """
        self.element_type: str = element_type
        self.content: str = content
        self.attributes: Dict[str, Any] = attributes or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the element to a dictionary representation.
        
        Returns:
            Dictionary representation of the element
        """
        return {
            'type': self.element_type,
            'content': self.content,
            'attributes': self.attributes
        }
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(content='{self.content[:20]}...', attributes={self.attributes})"
