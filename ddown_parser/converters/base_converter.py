from typing import Dict, List, Any, Optional


class BaseConverter:
    """Base class for all converters in the Ddown parser system.
    
    This class provides common functionality for converting Ddown elements
    to various output formats.
    """
    
    def __init__(self) -> None:
        """Initialize a new base converter."""
        pass
    
    def convert(self, document: Dict[str, Any]) -> Any:
        """Convert a parsed Ddown document to the target format.
        
        Args:
            document: Parsed Ddown document structure
            
        Returns:
            Converted document in the target format
        """
        raise NotImplementedError("Subclasses must implement the convert method")
