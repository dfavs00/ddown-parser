from typing import List, Dict, Any, Tuple, Optional, Pattern
import re


class DdownToken:
    """Represents a token in the Ddown document.
    
    A token is a basic unit of the document, such as a heading, paragraph,
    list item, etc., along with its attributes and styles.
    """
    
    def __init__(self, token_type: str, content: str, line_number: int, 
                 attributes: Optional[Dict[str, Any]] = None) -> None:
        """Initialize a new Ddown token.
        
        Args:
            token_type: Type of the token (heading, list_item, paragraph, etc.)
            content: Raw content of the token
            line_number: Line number where the token starts in the original document
            attributes: Additional attributes for the token (styles, classes, etc.)
        """
        self.token_type: str = token_type
        self.content: str = content
        self.line_number: int = line_number
        self.attributes: Dict[str, Any] = attributes or {}
    
    def __repr__(self) -> str:
        return f"DdownToken({self.token_type}, line={self.line_number}, content='{self.content[:20]}...')"


class DdownTokenizer:
    """Tokenizes Ddown content into a list of tokens.
    
    This class is responsible for breaking down the raw Ddown content
    into tokens that can be processed by the parser.
    """
    
    def __init__(self) -> None:
        # Initialize regex patterns for different Ddown elements
        self.patterns: Dict[str, Pattern] = self._compile_patterns()
    
    def _compile_patterns(self) -> Dict[str, Pattern]:
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
            
            # Paragraph (any text not matching other patterns)
            'paragraph': re.compile(r'^([^\n]+)$', re.MULTILINE),
        }
    
    def tokenize(self, content: str) -> Tuple[List[DdownToken], Optional[str]]:
        """Tokenize the Ddown content into a list of tokens.
        
        Args:
            content: Raw Ddown content as a string
            
        Returns:
            A tuple containing:
            - List of DdownToken objects
            - Global style string (if present, otherwise None)
        """
        # Extract global style if present
        global_style = self._extract_global_style(content)
        if global_style:
            # Remove global style from content to avoid tokenizing it
            content = self.patterns['style_global'].sub('', content)
        
        # Initialize tokens list
        tokens: List[DdownToken] = []
        
        # Process the content line by line to create tokens
        # This is a simplified approach - a complete tokenizer would be more sophisticated
        lines = content.split('\n')
        line_index = 0
        
        while line_index < len(lines):
            line = lines[line_index]
            
            # TODO: Implement tokenization logic for each element type
            # For now, create a simple paragraph token for each non-empty line
            if line.strip():
                tokens.append(DdownToken('paragraph', line, line_index))
            
            line_index += 1
        
        return tokens, global_style
    
    def _extract_global_style(self, content: str) -> Optional[str]:
        """Extract global style definitions from the content.
        
        Args:
            content: Raw Ddown content
            
        Returns:
            CSS style string or None if no global style is defined
        """
        match = self.patterns['style_global'].search(content)
        if match:
            return match.group(1).strip()
        return None
    
    def _extract_inline_style(self, content: str) -> Tuple[str, Optional[Dict[str, str]]]:
        """Extract inline style from content.
        
        Args:
            content: Content that may contain inline style
            
        Returns:
            Tuple of (content without style markup, style dict or None)
        """
        style_dict = None
        match = self.patterns['style_inline'].search(content)
        
        if match:
            style_text = match.group(1)
            # Parse the CSS-like style text into a dictionary
            style_dict = {}
            for style_item in style_text.split(';'):
                if ':' in style_item:
                    key, value = style_item.split(':', 1)
                    style_dict[key.strip()] = value.strip()
            
            # Remove the style markup from the content
            content = self.patterns['style_inline'].sub('', content)
        
        return content, style_dict
    
    def _extract_class_id(self, content: str) -> Tuple[str, Optional[Dict[str, str]]]:
        """Extract class and ID attributes from content.
        
        Args:
            content: Content that may contain class/ID markup
            
        Returns:
            Tuple of (content without class/ID markup, attributes dict or None)
        """
        attributes = None
        match = self.patterns['class_id'].search(content)
        
        if match:
            attr_text = match.group(1)
            attributes = {'classes': [], 'id': None}
            
            # Parse class and ID attributes
            for attr in attr_text.split():
                if attr.startswith('.'):
                    attributes['classes'].append(attr[1:])
                elif attr.startswith('#'):
                    attributes['id'] = attr[1:]
            
            # Remove the attribute markup from the content
            content = self.patterns['class_id'].sub('', content)
        
        return content, attributes
