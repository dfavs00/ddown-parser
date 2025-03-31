from typing import Dict, List, Any, Optional, Tuple, Union
import re


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


class ParagraphElement(DdownElement):
    """Represents a paragraph element in the Ddown document."""
    
    def __init__(self, content: str, attributes: Optional[Dict[str, Any]] = None) -> None:
        """Initialize a new paragraph element.
        
        Args:
            content: Content of the paragraph
            attributes: Additional attributes for the paragraph
        """
        super().__init__('paragraph', content, attributes)


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


class BlockquoteElement(DdownElement):
    """Represents a blockquote element in the Ddown document."""
    
    def __init__(self, content: str, attributes: Optional[Dict[str, Any]] = None) -> None:
        """Initialize a new blockquote element.
        
        Args:
            content: Content of the blockquote
            attributes: Additional attributes for the blockquote
        """
        super().__init__('blockquote', content, attributes)


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
        attributes_str = ''
        if self.attributes:
            for key, value in self.attributes.items():
                if key == 'style':
                    style_str = '; '.join([f"{k}: {v}" for k, v in value.items()])
                    attributes_str += f" style=\"{style_str}\""
                elif key == 'classes':
                    class_str = ' '.join(value)
                    attributes_str += f" class=\"{class_str}\""
                elif key == 'id':
                    attributes_str += f" id=\"{value}\""
                else:
                    attributes_str += f" {key}=\"{value}\""
        
        return f"<img src=\"{self.src}\" alt=\"{self.alt}\"{attributes_str}>"


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
        attributes_str = ''
        if self.attributes:
            for key, value in self.attributes.items():
                if key == 'style':
                    style_str = '; '.join([f"{k}: {v}" for k, v in value.items()])
                    attributes_str += f" style=\"{style_str}\""
                elif key == 'classes':
                    class_str = ' '.join(value)
                    attributes_str += f" class=\"{class_str}\""
                elif key == 'id':
                    attributes_str += f" id=\"{value}\""
                else:
                    attributes_str += f" {key}=\"{value}\""
        
        return f"<a href=\"{self.href}\"{attributes_str}>{self.content}</a>"


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


class ElementParser:
    """Parser for converting raw Ddown content into structured elements."""
    
    def __init__(self) -> None:
        # Compile regex patterns for different Ddown elements
        self.patterns: Dict[str, re.Pattern] = self._compile_patterns()
    
    def _compile_patterns(self) -> Dict[str, re.Pattern]:
        """Compile regex patterns for different Ddown elements.
        
        Returns:
            Dictionary of compiled regex patterns
        """
        return {
            # Heading patterns
            'heading_h1': re.compile(r'^(.+)\n={3,}\s*$', re.MULTILINE),
            'heading_h2': re.compile(r'^(.+)\n-{3,}\s*$', re.MULTILINE),
            'heading_h3': re.compile(r'^(.+)\n~{3,}\s*$', re.MULTILINE),
            'heading_h4': re.compile(r'^(.+)\n\^{3,}\s*$', re.MULTILINE),
            'heading_h5': re.compile(r'^(.+)\n\*{3,}\s*$', re.MULTILINE),
            
            # List patterns
            'list_unordered': re.compile(r'^=>\s+(.+)$', re.MULTILINE),
            'list_ordered': re.compile(r'^(\d+)\.\s+(.+)$', re.MULTILINE),
            
            # Style patterns
            'style_global': re.compile(r'\{@global-style\}([\s\S]*?)\{@endglobal-style\}'),
            'style_inline': re.compile(r'\{@\s*([^}]+)\s*\}'),
            'class_id': re.compile(r'\{([#.][^}]+)\}'),
            
            # Other elements
            'code_block': re.compile(r'```([^\n]*)\n([\s\S]*?)```', re.MULTILINE),
            'blockquote': re.compile(r'^>\s+(.+)$', re.MULTILINE),
            'image': re.compile(r'!\[(.*?)\]\((.*?)\)'),
            'link': re.compile(r'\[(.*?)\]\((.*?)\)'),
            'table': re.compile(r'^\|(.+)\|\s*$\n^\|[-|\s]+\|\s*$\n((?:^\|.+\|\s*$\n?)+)', 
                                re.MULTILINE),
        }
    
    def parse_heading(self, content: str, match: re.Match, level: int) -> HeadingElement:
        """Parse a heading element from a regex match.
        
        Args:
            content: Original content containing the heading
            match: Regex match object for the heading
            level: Heading level (1-5)
            
        Returns:
            Parsed HeadingElement
        """
        heading_text = match.group(1).strip()
        
        # Extract inline styles and class/id if present
        attributes = {}
        
        # Check for inline style
        style_match = self.patterns['style_inline'].search(heading_text)
        if style_match:
            style_text = style_match.group(1)
            # Parse the CSS-like style text into a dictionary
            style_dict = {}
            for style_item in style_text.split(';'):
                if ':' in style_item:
                    key, value = style_item.split(':', 1)
                    style_dict[key.strip()] = value.strip()
            
            attributes['style'] = style_dict
            # Remove the style markup from the heading text
            heading_text = self.patterns['style_inline'].sub('', heading_text)
        
        # Check for class/id
        class_id_match = self.patterns['class_id'].search(heading_text)
        if class_id_match:
            attr_text = class_id_match.group(1)
            classes = []
            id_value = None
            
            # Parse class and ID attributes
            for attr in attr_text.split():
                if attr.startswith('.'):
                    classes.append(attr[1:])
                elif attr.startswith('#'):
                    id_value = attr[1:]
            
            if classes:
                attributes['classes'] = classes
            if id_value:
                attributes['id'] = id_value
            
            # Remove the attribute markup from the heading text
            heading_text = self.patterns['class_id'].sub('', heading_text)
        
        return HeadingElement(heading_text.strip(), level, attributes)
    
    def parse_list_items(self, content: str) -> List[ListItemElement]:
        """Parse list items from content.
        
        Args:
            content: Content containing list items
            
        Returns:
            List of parsed ListItemElement objects
        """
        list_items = []
        
        # Parse unordered list items
        unordered_matches = list(self.patterns['list_unordered'].finditer(content))
        if unordered_matches:
            # Group consecutive unordered list items
            current_list = []
            list_attributes = {}
            
            for i, match in enumerate(unordered_matches):
                item_text = match.group(1).strip()
                
                # Extract inline styles and class/id if present
                attributes = {}
                
                # Check for inline style
                style_match = self.patterns['style_inline'].search(item_text)
                if style_match:
                    # Parse inline style
                    # (Implementation similar to parse_heading)
                    pass
                
                # Check for class/id
                class_id_match = self.patterns['class_id'].search(item_text)
                if class_id_match:
                    # Parse class/id
                    # (Implementation similar to parse_heading)
                    pass
                
                # Determine if this is the first or last item in the list
                first_in_list = not current_list
                
                # Check if this is the last item in the list
                last_in_list = (i == len(unordered_matches) - 1)
                if not last_in_list:
                    # Check if the next item is part of the same list
                    # (This is a simplified check - a real implementation would be more robust)
                    pass
                
                # Create list item element
                list_item = ListItemElement(
                    content=item_text,
                    list_type='unordered',
                    first_in_list=first_in_list,
                    last_in_list=last_in_list,
                    list_attributes=list_attributes,
                    attributes=attributes
                )
                
                list_items.append(list_item)
                current_list.append(list_item)
        
        # Parse ordered list items (similar implementation)
        # ...
        
        return list_items
    
    # Additional parsing methods for other element types would be implemented here
    # ...
