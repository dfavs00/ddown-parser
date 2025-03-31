from typing import Dict, Any, List


def build_html_attributes(attributes: Dict[str, Any]) -> str:
    """Build HTML attribute string from attributes dictionary.
    
    Args:
        attributes: Dictionary of attributes
        
    Returns:
        String of HTML attributes with leading space if not empty
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
