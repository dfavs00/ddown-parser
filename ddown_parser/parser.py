from typing import Dict, List, Optional, Union, Any, Tuple, IO
from io import BytesIO
import re
from pathlib import Path
from .elements import (
    DdownElement, HeadingElement, ParagraphElement, ListItemElement,
    CodeBlockElement, BlockquoteElement, ImageElement, LinkElement, TableElement, ElementParser
)


class DdownParser:
    """Main parser class for converting Ddown files to various output formats.
    
    This class handles parsing Ddown syntax into an intermediate representation
    and then converting that representation to the requested output format.
    """
    
    def __init__(self) -> None:
        # Initialize regex patterns for different Ddown elements
        self.heading_patterns: Dict[str, re.Pattern] = {
            'h1': re.compile(r'^(.+)\n(={3,})\s*$', re.MULTILINE),
            'h2': re.compile(r'^(.+)\n(-{3,})\s*$', re.MULTILINE),
            'h3': re.compile(r'^(.+)\n(~{3,})\s*$', re.MULTILINE),
            'h4': re.compile(r'^(.+)\n(\^{3,})\s*$', re.MULTILINE),
            'h5': re.compile(r'^(.+)\n(\*{3,})\s*$', re.MULTILINE),
        }
        self.list_patterns: Dict[str, re.Pattern] = {
            'unordered': re.compile(r'^=>\s+(.+)$', re.MULTILINE),
            'ordered': re.compile(r'^(\d+)\.\s+(.+)$', re.MULTILINE),
        }
        self.style_patterns: Dict[str, re.Pattern] = {
            'global': re.compile(r'\{@global-style\}([\s\S]*?)\{@endglobal-style\}'),
            'inline': re.compile(r'\{@\s*([^}]+)\s*\}'),
            'class_id': re.compile(r'\{([#.][^}]+)\}'),
        }
        
        # Initialize the element parser
        self.element_parser = ElementParser()
        
        # Initialize supported output formats
        self.output_formats: List[str] = ['html', 'pdf']
    
    def parse_file(self, file_path: Union[str, Path], output_format: str = 'html') -> Union[str, bytes]:
        """Parse a Ddown file and convert it to the specified output format.
        
        Args:
            file_path: Path to the Ddown file to parse
            output_format: Output format (html, pdf, etc.)
            
        Returns:
            Parsed content in the requested format (string for HTML, bytes for PDF)
            
        Raises:
            ValueError: If the output format is not supported
            FileNotFoundError: If the input file doesn't exist
        """
        if output_format not in self.output_formats:
            raise ValueError(f"Unsupported output format: {output_format}. "  
                             f"Supported formats: {', '.join(self.output_formats)}")
        
        # Convert string path to Path object for better handling
        path = Path(file_path) if isinstance(file_path, str) else file_path
        
        if not path.exists():
            raise FileNotFoundError(f"File not found: {path}")
        
        # Read the file content
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Parse the content to an intermediate representation
        document = self._parse_content(content)
        
        # Convert to the requested output format
        if output_format == 'html':
            return self._convert_to_html(document)
        elif output_format == 'pdf':
            return self._convert_to_pdf(document)
    
    def _parse_content(self, content: str) -> Dict[str, Any]:
        """Parse Ddown content into an intermediate representation.
        
        Args:
            content: Raw Ddown content as a string
            
        Returns:
            A dictionary representing the parsed document structure
        """
        # Extract global styles if present
        global_style = self._extract_global_style(content)
        
        # Create document structure
        document = {
            'global_style': global_style,
            'elements': self._parse_elements(content),
        }
        
        return document
    
    def _extract_global_style(self, content: str) -> Optional[str]:
        """Extract global style definitions from the content.
        
        Args:
            content: Raw Ddown content
            
        Returns:
            CSS style string or None if no global style is defined
        """
        match = self.style_patterns['global'].search(content)
        if match:
            return match.group(1).strip()
        return None
    
    def _parse_elements(self, content: str) -> List[Dict[str, Any]]:
        """Parse all elements from the Ddown content.
        
        This method coordinates the parsing of different element types and
        ensures they are returned in the correct order.
        
        Args:
            content: Raw Ddown content
            
        Returns:
            List of parsed elements with their attributes
        """
        # Remove global style section if present to avoid parsing it as content
        content = self.style_patterns['global'].sub('', content)
        
        # Split content into lines for line-by-line processing
        lines = content.split('\n')
        processed_lines = [False] * len(lines)
        
        # Parse all elements with their positions in the document
        elements_with_position = []
        
        # Parse each type of element
        self._parse_headings(content, lines, processed_lines, elements_with_position)
        self._parse_code_blocks(content, lines, processed_lines, elements_with_position)
        self._parse_blockquotes(lines, processed_lines, elements_with_position)
        self._parse_tables(content, lines, processed_lines, elements_with_position)
        self._parse_unordered_lists(lines, processed_lines, elements_with_position)
        self._parse_ordered_lists(lines, processed_lines, elements_with_position)
        self._parse_paragraphs(lines, processed_lines, elements_with_position)
        
        # Sort elements by their original position in the document
        elements_with_position.sort(key=lambda x: x['position'])
        
        # Extract just the elements
        elements = [item['element'] for item in elements_with_position]
        
        return elements
    
    def _parse_headings(self, content: str, lines: List[str], 
                       processed_lines: List[bool], 
                       elements_with_position: List[Dict[str, Any]]) -> None:
        """Parse heading elements from the content.
        
        Args:
            content: Raw Ddown content
            lines: Content split into lines
            processed_lines: Tracking which lines have been processed
            elements_with_position: List to append parsed elements with their positions
        """
        for level, pattern in self.heading_patterns.items():
            for match in pattern.finditer(content):
                heading_text = match.group(1).strip()
                underline = match.group(2).strip()
                
                # Calculate line positions
                start_line = content[:match.start()].count('\n')
                end_line = start_line + 1  # Heading text line
                underline_line = end_line + 1  # Underline line
                
                # Check if there's a style after the underline
                style_attributes = self._extract_style_after_element(
                    lines, processed_lines, underline_line + 1)
                
                # Mark the heading lines as processed
                processed_lines[start_line:underline_line+1] = [True] * (underline_line - start_line + 1)
                
                # Extract inline styles and class/id from the heading text
                attributes = style_attributes.copy()
                heading_text, inline_attributes = self._extract_inline_attributes(heading_text)
                
                # Merge attributes
                if inline_attributes:
                    for key, value in inline_attributes.items():
                        if key in attributes and key == 'style':
                            # Merge style dictionaries
                            attributes[key].update(value)
                        else:
                            attributes[key] = value
                
                # Create the heading element
                heading = HeadingElement(
                    content=heading_text,
                    level=int(level[1]),  # Extract the number from 'h1', 'h2', etc.
                    attributes=attributes
                )
                
                # Add the heading element with its position
                elements_with_position.append({
                    'position': start_line,
                    'element': heading.to_dict()
                })
    
    def _extract_style_after_element(self, lines: List[str], 
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
        
        if style_line < len(lines) and self.style_patterns['inline'].search(lines[style_line]):
            style_match = self.style_patterns['inline'].search(lines[style_line])
            if style_match:
                style_text = style_match.group(1)
                # Parse the CSS-like style text into a dictionary
                style_dict = {}
                for style_item in style_text.split(';'):
                    if ':' in style_item:
                        key, value = style_item.split(':', 1)
                        style_dict[key.strip()] = value.strip()
                
                style_attributes['style'] = style_dict
                # Mark the style line as processed
                processed_lines[style_line] = True
        
        return style_attributes
    
    def _extract_inline_attributes(self, text: str) -> Tuple[str, Dict[str, Any]]:
        """Extract inline style and class/id attributes from text.
        
        Args:
            text: Text to extract attributes from
            
        Returns:
            Tuple of (cleaned text, extracted attributes)
        """
        attributes = {}
        
        # Check for inline style
        style_match = self.style_patterns['inline'].search(text)
        if style_match:
            style_text = style_match.group(1)
            # Parse the CSS-like style text into a dictionary
            style_dict = {}
            for style_item in style_text.split(';'):
                if ':' in style_item:
                    key, value = style_item.split(':', 1)
                    style_dict[key.strip()] = value.strip()
            
            attributes['style'] = style_dict
            # Remove the style markup from the text
            text = self.style_patterns['inline'].sub('', text)
        
        # Check for class/id
        class_id_match = self.style_patterns['class_id'].search(text)
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
            
            # Remove the attribute markup from the text
            text = self.style_patterns['class_id'].sub('', text)
        
        return text.strip(), attributes
    
    def _process_inline_elements(self, text: str) -> str:
        """Process inline elements like links and images in text.
        
        Args:
            text: Text to process
            
        Returns:
            Text with inline elements converted to HTML
        """
        # Process links
        link_pattern = re.compile(r'\[(.*?)\]\((.*?)\)')
        for link_match in link_pattern.finditer(text):
            link_text = link_match.group(1)
            link_url = link_match.group(2)
            text = text.replace(link_match.group(0), f'<a href="{link_url}">{link_text}</a>')
        
        # Process images
        image_pattern = re.compile(r'!\[(.*?)\]\((.*?)\)')
        for image_match in image_pattern.finditer(text):
            alt_text = image_match.group(1)
            image_url = image_match.group(2)
            text = text.replace(image_match.group(0), f'<img src="{image_url}" alt="{alt_text}">')
        
        return text
    
    def _parse_code_blocks(self, content: str, lines: List[str], 
                          processed_lines: List[bool], 
                          elements_with_position: List[Dict[str, Any]]) -> None:
        """Parse code block elements from the content.
        
        Args:
            content: Raw Ddown content
            lines: Content split into lines
            processed_lines: Tracking which lines have been processed
            elements_with_position: List to append parsed elements with their positions
        """
        code_block_pattern = re.compile(r'```([^\n]*)\n([\s\S]*?)```', re.MULTILINE)
        for match in code_block_pattern.finditer(content):
            language = match.group(1).strip()
            code_content = match.group(2)
            
            # Calculate line positions
            start_line = content[:match.start()].count('\n')
            end_line = start_line + content[match.start():match.end()].count('\n')
            
            # Mark the code block lines as processed
            processed_lines[start_line:end_line+1] = [True] * (end_line - start_line + 1)
            
            # Create the code block element
            code_block = CodeBlockElement(
                content=code_content,
                language=language
            )
            
            # Add the code block element with its position
            elements_with_position.append({
                'position': start_line,
                'element': code_block.to_dict()
            })
    
    def _parse_blockquotes(self, lines: List[str], 
                          processed_lines: List[bool], 
                          elements_with_position: List[Dict[str, Any]]) -> None:
        """Parse blockquote elements from the content.
        
        Args:
            lines: Content split into lines
            processed_lines: Tracking which lines have been processed
            elements_with_position: List to append parsed elements with their positions
        """
        blockquote_lines = []
        blockquote_start_line = -1
        in_blockquote = False
        
        for i, line in enumerate(lines):
            if processed_lines[i]:
                # Skip already processed lines
                if in_blockquote and blockquote_lines:
                    # End of blockquote
                    blockquote = BlockquoteElement(
                        content='\n'.join(blockquote_lines)
                    )
                    elements_with_position.append({
                        'position': blockquote_start_line,
                        'element': blockquote.to_dict()
                    })
                    blockquote_lines = []
                    in_blockquote = False
                continue
                
            if line.strip().startswith('>'):
                # This is a blockquote line
                if not in_blockquote:
                    blockquote_start_line = i
                    in_blockquote = True
                blockquote_text = line.strip()[1:].strip()  # Remove '>' and leading/trailing whitespace
                blockquote_lines.append(blockquote_text)
                processed_lines[i] = True
            elif in_blockquote and line.strip():
                # Continuation of blockquote
                blockquote_lines.append(line.strip())
                processed_lines[i] = True
            elif in_blockquote:
                # End of blockquote
                blockquote = BlockquoteElement(
                    content='\n'.join(blockquote_lines)
                )
                elements_with_position.append({
                    'position': blockquote_start_line,
                    'element': blockquote.to_dict()
                })
                blockquote_lines = []
                in_blockquote = False
        
        # Don't forget the last blockquote if there is one
        if in_blockquote and blockquote_lines:
            blockquote = BlockquoteElement(
                content='\n'.join(blockquote_lines)
            )
            elements_with_position.append({
                'position': blockquote_start_line,
                'element': blockquote.to_dict()
            })
    
    def _parse_tables(self, content: str, lines: List[str], 
                     processed_lines: List[bool], 
                     elements_with_position: List[Dict[str, Any]]) -> None:
        """Parse table elements from the content.
        
        Args:
            content: Raw Ddown content
            lines: Content split into lines
            processed_lines: Tracking which lines have been processed
            elements_with_position: List to append parsed elements with their positions
        """
        table_pattern = re.compile(r'^\|(.+)\|\s*$\n^\|[-|\s]+\|\s*$\n((?:^\|.+\|\s*$\n?)+)', re.MULTILINE)
        for match in table_pattern.finditer(content):
            header_row = [cell.strip() for cell in match.group(1).split('|') if cell.strip()]
            data_rows_text = match.group(2)
            
            # Parse data rows
            data_rows = []
            for row_text in data_rows_text.strip().split('\n'):
                if row_text.strip().startswith('|') and row_text.strip().endswith('|'):
                    row_cells = [cell.strip() for cell in row_text.strip()[1:-1].split('|')]
                    data_rows.append(row_cells)
            
            # Calculate line positions
            start_line = content[:match.start()].count('\n')
            end_line = start_line + content[match.start():match.end()].count('\n')
            
            # Mark the table lines as processed
            processed_lines[start_line:end_line+1] = [True] * (end_line - start_line + 1)
            
            # Create the table element
            # Combine header and data rows for the TableElement
            all_rows = [header_row] + data_rows
            table = TableElement(rows=all_rows)
            
            # Add the table element with its position
            elements_with_position.append({
                'position': start_line,
                'element': table.to_dict()
            })
    
    def _parse_unordered_lists(self, lines: List[str], 
                              processed_lines: List[bool], 
                              elements_with_position: List[Dict[str, Any]]) -> None:
        """Parse unordered list elements from the content.
        
        Args:
            lines: Content split into lines
            processed_lines: Tracking which lines have been processed
            elements_with_position: List to append parsed elements with their positions
        """
        list_items = []
        list_start_line = -1
        
        for i, line in enumerate(lines):
            if processed_lines[i]:
                # Skip already processed lines
                continue
                
            if line.strip().startswith('=>'):
                # This is an unordered list item
                if list_start_line == -1:
                    list_start_line = i
                    
                item_text = line.strip()[2:].strip()  # Remove '=>' and leading/trailing whitespace
                
                # Extract inline styles and class/id
                item_text, attributes = self._extract_inline_attributes(item_text)
                
                # Process links and images
                item_text = self._process_inline_elements(item_text)
                
                # Create the list item
                list_item = ListItemElement(
                    content=item_text,
                    list_type='unordered',
                    attributes=attributes,
                    first_in_list=len(list_items) == 0
                )
                list_items.append(list_item)
                
                processed_lines[i] = True
        
        # If we found any list items, create a list element
        if list_items:
            # Mark the last item
            list_items[-1].last_in_list = True
            
            # Convert list items to dictionaries
            items_dict = [item.to_dict() for item in list_items]
            
            # Add the list element with its position
            elements_with_position.append({
                'position': list_start_line,
                'element': {
                    'type': 'list',
                    'list_type': 'unordered',
                    'items': items_dict,
                    'attributes': {}
                }
            })
    
    def _parse_ordered_lists(self, lines: List[str], 
                           processed_lines: List[bool], 
                           elements_with_position: List[Dict[str, Any]]) -> None:
        """Parse ordered list elements from the content.
        
        Args:
            lines: Content split into lines
            processed_lines: Tracking which lines have been processed
            elements_with_position: List to append parsed elements with their positions
        """
        ordered_items = []
        ordered_list_start_line = -1
        ordered_list_pattern = re.compile(r'^(\d+)\.\s+(.+)$')
        
        for i, line in enumerate(lines):
            if processed_lines[i]:
                # Skip already processed lines
                continue
                
            match = ordered_list_pattern.match(line.strip())
            if match:
                # This is an ordered list item
                if ordered_list_start_line == -1:
                    ordered_list_start_line = i
                    
                item_number = int(match.group(1))
                item_text = match.group(2).strip()
                
                # Extract inline styles and class/id
                item_text, attributes = self._extract_inline_attributes(item_text)
                
                # Process links and images
                item_text = self._process_inline_elements(item_text)
                
                # Create the list item
                list_item = ListItemElement(
                    content=item_text,
                    list_type='ordered',
                    list_index=item_number,
                    attributes=attributes,
                    first_in_list=len(ordered_items) == 0
                )
                ordered_items.append(list_item)
                
                processed_lines[i] = True
        
        # If we found any ordered list items, create a list element
        if ordered_items:
            # Mark the last item
            ordered_items[-1].last_in_list = True
            
            # Convert list items to dictionaries
            items_dict = [item.to_dict() for item in ordered_items]
            
            # Add the list element with its position
            elements_with_position.append({
                'position': ordered_list_start_line,
                'element': {
                    'type': 'list',
                    'list_type': 'ordered',
                    'items': items_dict,
                    'attributes': {}
                }
            })
    
    def _parse_paragraphs(self, lines: List[str], 
                         processed_lines: List[bool], 
                         elements_with_position: List[Dict[str, Any]]) -> None:
        """Parse paragraph elements from the content.
        
        Args:
            lines: Content split into lines
            processed_lines: Tracking which lines have been processed
            elements_with_position: List to append parsed elements with their positions
        """
        paragraph_lines = []
        paragraph_start_line = -1
        
        for i, line in enumerate(lines):
            if processed_lines[i]:
                # Skip already processed lines
                if paragraph_lines:
                    # End of paragraph
                    paragraph_text = ' '.join(paragraph_lines)
                    
                    # Process links and images
                    paragraph_text = self._process_inline_elements(paragraph_text)
                    
                    # Create the paragraph element
                    paragraph = ParagraphElement(content=paragraph_text)
                    
                    elements_with_position.append({
                        'position': paragraph_start_line,
                        'element': paragraph.to_dict()
                    })
                    paragraph_lines = []
                    paragraph_start_line = -1
                continue
                
            if not line.strip():
                # Empty line ends a paragraph
                if paragraph_lines:
                    paragraph_text = ' '.join(paragraph_lines)
                    
                    # Process links and images
                    paragraph_text = self._process_inline_elements(paragraph_text)
                    
                    # Create the paragraph element
                    paragraph = ParagraphElement(content=paragraph_text)
                    
                    elements_with_position.append({
                        'position': paragraph_start_line,
                        'element': paragraph.to_dict()
                    })
                    paragraph_lines = []
                    paragraph_start_line = -1
            else:
                # Add to current paragraph
                if not paragraph_lines:
                    paragraph_start_line = i
                paragraph_lines.append(line.strip())
                processed_lines[i] = True
        
        # Don't forget the last paragraph if there is one
        if paragraph_lines:
            paragraph_text = ' '.join(paragraph_lines)
            
            # Process links and images
            paragraph_text = self._process_inline_elements(paragraph_text)
            
            # Create the paragraph element
            paragraph = ParagraphElement(content=paragraph_text)
            
            elements_with_position.append({
                'position': paragraph_start_line,
                'element': paragraph.to_dict()
            })
    
    def _convert_to_html(self, document: Dict[str, Any]) -> str:
        """Convert the parsed document to HTML.
        
        Args:
            document: Parsed document structure
            
        Returns:
            HTML string representation of the document
        """
        # Start with HTML document structure
        html = ["<!DOCTYPE html>", "<html>", "<head>", "<meta charset=\"UTF-8\">", 
                "<title>Ddown Document</title>"]
        
        # Add global styles if present
        if document['global_style']:
            html.append(f"<style>{document['global_style']}</style>")
        
        html.append("</head>")
        html.append("<body>")
        
        # Render each element in the document
        for element in document.get('elements', []):
            element_type = element.get('type')
            
            if element_type == 'heading':
                level = element.get('level', 1)  # Default to h1 if level not specified
                content = element.get('content', '')
                attributes = self._build_html_attributes(element.get('attributes', {}))
                html.append(f"<h{level}{attributes}>{content}</h{level}>")
            
            elif element_type == 'paragraph':
                content = element.get('content', '')
                attributes = self._build_html_attributes(element.get('attributes', {}))
                html.append(f"<p{attributes}>{content}</p>")
            
            elif element_type == 'list':
                list_type = element.get('list_type', 'unordered')  # 'ordered' or 'unordered'
                list_items = element.get('items', [])
                attributes = self._build_html_attributes(element.get('attributes', {}))
                
                # Start the list
                list_tag = 'ol' if list_type == 'ordered' else 'ul'
                html.append(f"<{list_tag}{attributes}>")
                
                # Add each list item
                for item in list_items:
                    item_content = item.get('content', '')
                    item_attributes = self._build_html_attributes(item.get('attributes', {}))
                    html.append(f"<li{item_attributes}>{item_content}</li>")
                
                # End the list
                html.append(f"</{list_tag}>")
            
            elif element_type == 'code_block':
                content = element.get('content', '')
                language = element.get('language', '')
                attributes = self._build_html_attributes(element.get('attributes', {}))
                
                # Add language class if specified
                if language:
                    class_attr = f" class=\"language-{language}\""
                else:
                    class_attr = ""
                
                # Escape HTML entities in code content
                content = content.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
                
                html.append(f"<pre{attributes}><code{class_attr}>{content}</code></pre>")
            
            elif element_type == 'blockquote':
                content = element.get('content', '')
                attributes = self._build_html_attributes(element.get('attributes', {}))
                html.append(f"<blockquote{attributes}>{content}</blockquote>")
            
            elif element_type == 'table':
                rows = element.get('rows', [])
                attributes = self._build_html_attributes(element.get('attributes', {}))
                
                if not rows:
                    continue  # Skip empty tables
                
                table_html = [f"<table{attributes}>"]
                
                # First row is the header
                header_row = rows[0] if rows else []
                if header_row:
                    table_html.append("<thead>")
                    table_html.append("<tr>")
                    for cell in header_row:
                        table_html.append(f"<th>{cell}</th>")
                    table_html.append("</tr>")
                    table_html.append("</thead>")
                
                # Data rows
                if len(rows) > 1:
                    table_html.append("<tbody>")
                    for row in rows[1:]:  # Skip header row
                        table_html.append("<tr>")
                        for cell in row:
                            table_html.append(f"<td>{cell}</td>")
                        table_html.append("</tr>")
                    table_html.append("</tbody>")
                
                table_html.append("</table>")
                html.extend(table_html)
            
            elif element_type == 'image':
                alt = element.get('alt', '')
                src = element.get('src', '')
                attributes = self._build_html_attributes(element.get('attributes', {}))
                html.append(f"<img src=\"{src}\" alt=\"{alt}\"{attributes}>")
            
            elif element_type == 'link':
                content = element.get('content', '')
                href = element.get('href', '')
                attributes = self._build_html_attributes(element.get('attributes', {}))
                html.append(f"<a href=\"{href}\"{attributes}>{content}</a>")
        
        html.append("</body>")
        html.append("</html>")
        
        return "\n".join(html)

    def _build_html_attributes(self, attributes: Dict[str, Any]) -> str:
        """Build HTML attribute string from attributes dictionary.
        
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
                style_str = "; ".join(style_items)
                attr_parts.append(f"style=\"{style_str}\"")
        
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

    def _convert_to_pdf(self, document: Dict[str, Any]) -> bytes:
        """Convert the parsed document to PDF.
        
        Args:
            document: Parsed document structure
            
        Returns:
            PDF content as bytes
        """
        # First convert to HTML
        html = self._convert_to_html(document)
        
        # Then convert HTML to PDF using WeasyPrint
        # This is a placeholder - in a real implementation, we would use WeasyPrint here
        # from weasyprint import HTML
        # pdf_bytes = HTML(string=html).write_pdf()
        
        # For now, return empty bytes
        return b""  # Placeholder
