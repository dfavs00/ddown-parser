from typing import Dict, List, Any, Optional, Tuple, Pattern, Match
import re


class BaseParser:
    """Base class for all parsers in the Ddown parser system.
    
    This class provides common functionality for parsing Ddown elements.
    """
    
    def __init__(self) -> None:
        """Initialize a new base parser."""
        # Compile regex patterns for different Ddown elements
        self.heading_patterns: Dict[str, Pattern] = {
            'h1': re.compile(r'^(.+?)\n(={3,})\s*$', re.MULTILINE),
            'h2': re.compile(r'^(.+?)\n(-{3,})\s*$', re.MULTILINE),
            'h3': re.compile(r'^(.+?)\n(~{3,})\s*$', re.MULTILINE),
            'h4': re.compile(r'^(.+?)\n(\^{3,})\s*$', re.MULTILINE),
            'h5': re.compile(r'^(.+?)\n(\*{3,})\s*$', re.MULTILINE),
        }
        self.list_patterns: Dict[str, Pattern] = {
            'unordered': re.compile(r'^=>\s+(.+)$', re.MULTILINE),
            'ordered': re.compile(r'^(\d+)\.\s+(.+)$', re.MULTILINE),
        }
        self.style_patterns: Dict[str, Pattern] = {
            'global': re.compile(r'\{@global-style\}([\s\S]*?)\{@endglobal-style\}'),
            'inline': re.compile(r'\{@\s*([^}]+)\s*\}'),
            'class_id': re.compile(r'\{([#.][^}]+)\}'),
            'dom_mode': re.compile(r'\{@dom-mode\}'),  # New pattern for dom-mode
        }
        self.code_block_pattern: Pattern = re.compile(r'```([^\n]*)\n([\s\S]*?)```', re.MULTILINE)
        self.blockquote_pattern: Pattern = re.compile(r'^>\s*(.+)$', re.MULTILINE)
        self.table_pattern: Pattern = re.compile(r'^\|(.+)\|\s*$', re.MULTILINE)
        self.table_separator_pattern: Pattern = re.compile(r'^\|[-:\s|]+\|\s*$', re.MULTILINE)
        self.link_pattern: Pattern = re.compile(r'\[(.*?)\]\((.*?)\)')
        self.image_pattern: Pattern = re.compile(r'!\[(.*?)\]\((.*?)\)')
    
    def extract_style_after_element(self, lines: List[str], 
                                   processed_lines: List[bool], 
                                   style_line: int) -> Dict[str, Any]:
        """Extract style attributes that appear on the line after an element.
        
        Args:
            lines: Content split into lines
            processed_lines: Tracking which lines have been processed
            style_line: Line number to check for style attributes
            
        Returns:
            Dictionary of extracted style attributes
        """
        style_attributes = {}
        
        if style_line < len(lines) and not processed_lines[style_line]:
            line = lines[style_line].strip()
            
            # Check for inline style
            if line.startswith('{@') and line.endswith('}'): 
                # Extract style content
                style_content = line[2:-1].strip()
                style_dict = {}
                
                # Parse style properties
                for style_item in style_content.split(';'):
                    style_item = style_item.strip()
                    if not style_item:
                        continue
                    
                    try:
                        key, value = style_item.split(':', 1)
                        style_dict[key.strip()] = value.strip()
                    except ValueError:
                        # Skip invalid style items
                        continue
                
                if style_dict:
                    style_attributes['style'] = style_dict
                    processed_lines[style_line] = True
            
            # Check for class/ID
            elif line.startswith('{') and line.endswith('}') and ('#' in line or '.' in line):
                class_id_content = line[1:-1].strip()
                classes = []
                element_id = None
                
                # Parse class and ID selectors
                for selector in class_id_content.split():
                    if selector.startswith('.'):
                        classes.append(selector[1:])
                    elif selector.startswith('#'):
                        element_id = selector[1:]
                
                if classes:
                    style_attributes['classes'] = classes
                if element_id:
                    style_attributes['id'] = element_id
                
                processed_lines[style_line] = True
        
        return style_attributes
    
    def extract_inline_attributes(self, text: str) -> Tuple[str, Dict[str, Any]]:
        """Extract inline style and class/id attributes from text.
        
        Args:
            text: Text to extract attributes from
            
        Returns:
            Tuple of (cleaned text, extracted attributes)
        """
        attributes = {}
        cleaned_text = text
        
        # Process all inline styles
        while True:
            inline_style_match = self.style_patterns['inline'].search(cleaned_text)
            if not inline_style_match:
                break
                
            style_content = inline_style_match.group(1).strip()
            style_dict = {}
            
            # Parse style properties
            for style_item in style_content.split(';'):
                style_item = style_item.strip()
                if not style_item:
                    continue
                
                try:
                    key, value = style_item.split(':', 1)
                    style_dict[key.strip()] = value.strip()
                except ValueError:
                    # Skip invalid style items
                    continue
            
            if style_dict:
                if 'style' not in attributes:
                    attributes['style'] = {}
                attributes['style'].update(style_dict)
            
            # Remove the style from the text
            cleaned_text = cleaned_text.replace(inline_style_match.group(0), '')
        
        # Process all class/ID attributes
        while True:
            class_id_match = self.style_patterns['class_id'].search(cleaned_text)
            if not class_id_match:
                break
                
            class_id_content = class_id_match.group(1).strip()
            classes = []
            element_id = None
            
            # Parse class and ID selectors
            for selector in class_id_content.split():
                if selector.startswith('.'):
                    classes.append(selector[1:])
                elif selector.startswith('#'):
                    element_id = selector[1:]
            
            if classes:
                if 'classes' not in attributes:
                    attributes['classes'] = []
                attributes['classes'].extend(classes)
            if element_id:
                attributes['id'] = element_id  # Last ID wins if multiple
            
            # Remove the class/ID from the text
            cleaned_text = cleaned_text.replace(class_id_match.group(0), '')
        
        return cleaned_text.strip(), attributes
