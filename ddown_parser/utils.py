from typing import Dict, List, Any, Optional, Tuple, Union, Pattern
import re


def parse_inline_style(style_text: str) -> Dict[str, str]:
    """Parse CSS-like inline style text into a dictionary.
    
    Args:
        style_text: CSS-like style text (e.g., "color: red; font-size: 12px")
        
    Returns:
        Dictionary mapping style properties to values
    """
    style_dict: Dict[str, str] = {}
    
    # Skip empty style text
    if not style_text or style_text.isspace():
        return style_dict
    
    # Split by semicolons and process each style declaration
    for style_item in style_text.split(';'):
        style_item = style_item.strip()
        if not style_item:
            continue
            
        if ':' in style_item:
            key, value = style_item.split(':', 1)
            style_dict[key.strip()] = value.strip()
    
    return style_dict


def parse_class_id(attr_text: str) -> Dict[str, Any]:
    """Parse class and ID attributes from text.
    
    Args:
        attr_text: Text containing class and ID attributes (e.g., "#my-id .class1 .class2")
        
    Returns:
        Dictionary with 'classes' (list) and 'id' (string or None) keys
    """
    attributes: Dict[str, Any] = {'classes': [], 'id': None}
    
    # Skip empty attribute text
    if not attr_text or attr_text.isspace():
        return attributes
    
    # Process each attribute (class or ID)
    for attr in attr_text.split():
        attr = attr.strip()
        if not attr:
            continue
            
        if attr.startswith('.'):
            # Class attribute
            class_name = attr[1:]
            if class_name:
                attributes['classes'].append(class_name)
        elif attr.startswith('#'):
            # ID attribute
            id_value = attr[1:]
            if id_value:
                attributes['id'] = id_value
    
    return attributes


def extract_attributes(content: str, style_pattern: Pattern, class_id_pattern: Pattern) -> Tuple[str, Dict[str, Any]]:
    """Extract inline styles and class/ID attributes from content.
    
    Args:
        content: Content that may contain style and class/ID markup
        style_pattern: Compiled regex pattern for inline styles
        class_id_pattern: Compiled regex pattern for class/ID attributes
        
    Returns:
        Tuple of (content without markup, attributes dictionary)
    """
    attributes: Dict[str, Any] = {}
    
    # Extract inline style
    style_match = style_pattern.search(content)
    if style_match:
        style_text = style_match.group(1)
        style_dict = parse_inline_style(style_text)
        if style_dict:
            attributes['style'] = style_dict
        # Remove the style markup from the content
        content = style_pattern.sub('', content)
    
    # Extract class/ID attributes
    class_id_match = class_id_pattern.search(content)
    if class_id_match:
        attr_text = class_id_match.group(1)
        attr_dict = parse_class_id(attr_text)
        
        if attr_dict['classes']:
            attributes['classes'] = attr_dict['classes']
        if attr_dict['id']:
            attributes['id'] = attr_dict['id']
        
        # Remove the attribute markup from the content
        content = class_id_pattern.sub('', content)
    
    return content.strip(), attributes


def build_html_attributes(attributes: Dict[str, Any]) -> str:
    """Build HTML attribute string from attributes dictionary.
    
    Args:
        attributes: Dictionary of attributes
        
    Returns:
        String of HTML attributes (including leading space if not empty)
    """
    if not attributes:
        return ""
    
    attr_parts: List[str] = []
    
    # Handle style attributes
    if 'style' in attributes and attributes['style']:
        style_items = []
        for key, value in attributes['style'].items():
            style_items.append(f"{key}: {value}")
        if style_items:
            attr_parts.append(f"style=\"{'; '.join(style_items)}\"")
    
    # Handle class attributes
    if 'classes' in attributes and attributes['classes']:
        attr_parts.append(f"class=\"{' '.join(attributes['classes'])}\"")
    
    # Handle ID attribute
    if 'id' in attributes and attributes['id']:
        attr_parts.append(f"id=\"{attributes['id']}\"")
    
    # Handle other attributes
    for key, value in attributes.items():
        if key not in ['style', 'classes', 'id']:
            attr_parts.append(f"{key}=\"{value}\"")
    
    return f" {' '.join(attr_parts)}" if attr_parts else ""
