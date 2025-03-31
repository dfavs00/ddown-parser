from typing import Dict, List, Any, Optional, Tuple, Pattern, Match
import re
from .base_parser import BaseParser
from ..elements import (
    HeadingElement,
    ParagraphElement,
    ListItemElement,
    ListElement,
    CodeBlockElement,
    BlockquoteElement,
    ImageElement,
    LinkElement,
    TableElement
)


class ElementParser(BaseParser):
    """Parser for individual Ddown elements.
    
    This class handles parsing specific element types from Ddown content.
    """
    
    def parse_headings(self, content: str, lines: List[str], 
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
                try:
                    heading_text = match.group(1).strip()
                    underline = match.group(2).strip()
                    
                    # Calculate line positions
                    start_line = content[:match.start()].count('\n')
                    end_line = start_line + 1  # Heading text line
                    underline_line = end_line + 1  # Underline line
                    
                    # Check if there's a style after the underline
                    style_attributes = {}
                    if underline_line + 1 < len(lines):
                        next_line = lines[underline_line + 1].strip()
                        if next_line.startswith('{@') and next_line.endswith('}'):
                            # Extract inline style
                            style_content = next_line[2:-1].strip()
                            style_dict = {}
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
                                processed_lines[underline_line + 1] = True
                    
                    # Mark the heading lines as processed
                    processed_lines[start_line:underline_line+1] = [True] * (underline_line - start_line + 1)
                    
                    # Extract inline styles and class/id from the heading text
                    attributes = style_attributes.copy()
                    heading_text, inline_attributes = self.extract_inline_attributes(heading_text)
                    
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
                except (IndexError, ValueError) as e:
                    # Skip this heading if there's an error in parsing
                    print(f"Warning: Error parsing heading: {e}")
                    continue
    
    def process_inline_elements(self, text: str) -> List[Dict[str, Any]]:
        """Process inline elements like links and images in text.
        
        Args:
            text: Text to process
            
        Returns:
            List of inline elements found in the text
        """
        inline_elements = []
        
        # Process links
        for link_match in self.link_pattern.finditer(text):
            if text[link_match.start()-1:link_match.start()] == '!':
                # This is an image, will be handled by the image pattern
                continue
                
            link_text = link_match.group(1)
            link_url = link_match.group(2)
            
            link_element = LinkElement(
                content=link_text,
                href=link_url
            )
            
            inline_elements.append({
                'type': 'link',
                'element': link_element.to_dict(),
                'start': link_match.start(),
                'end': link_match.end(),
                'original': link_match.group(0)
            })
        
        # Process images
        for image_match in self.image_pattern.finditer(text):
            alt_text = image_match.group(1)
            image_url = image_match.group(2)
            
            image_element = ImageElement(
                alt=alt_text,
                src=image_url
            )
            
            inline_elements.append({
                'type': 'image',
                'element': image_element.to_dict(),
                'start': image_match.start(),
                'end': image_match.end(),
                'original': image_match.group(0)
            })
        
        # Sort by position in text
        inline_elements.sort(key=lambda x: x['start'])
        
        return inline_elements
    
    def parse_code_blocks(self, content: str, lines: List[str], 
                          processed_lines: List[bool], 
                          elements_with_position: List[Dict[str, Any]]) -> None:
        """Parse code block elements from the content.
        
        Args:
            content: Raw Ddown content
            lines: Content split into lines
            processed_lines: Tracking which lines have been processed
            elements_with_position: List to append parsed elements with their positions
        """
        for match in self.code_block_pattern.finditer(content):
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
    
    def parse_blockquotes(self, lines: List[str], 
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
        
        # Handle blockquote at the end of the document
        if in_blockquote and blockquote_lines:
            blockquote = BlockquoteElement(
                content='\n'.join(blockquote_lines)
            )
            elements_with_position.append({
                'position': blockquote_start_line,
                'element': blockquote.to_dict()
            })
    
    def parse_tables(self, content: str, lines: List[str], 
                     processed_lines: List[bool], 
                     elements_with_position: List[Dict[str, Any]]) -> None:
        """Parse table elements from the content.
        
        Args:
            content: Raw Ddown content
            lines: Content split into lines
            processed_lines: Tracking which lines have been processed
            elements_with_position: List to append parsed elements with their positions
        """
        table_rows = []
        table_start_line = -1
        in_table = False
        
        for i, line in enumerate(lines):
            if processed_lines[i]:
                # Skip already processed lines
                if in_table and table_rows:
                    # End of table
                    table = TableElement(rows=table_rows)
                    elements_with_position.append({
                        'position': table_start_line,
                        'element': table.to_dict()
                    })
                    table_rows = []
                    in_table = False
                continue
            
            line = line.strip()
            if line.startswith('|') and line.endswith('|'):
                # This is a table row
                if not in_table:
                    table_start_line = i
                    in_table = True
                
                # Check if this is a separator row
                if self.table_separator_pattern.match(line):
                    processed_lines[i] = True
                    continue
                
                # Parse the cells
                cells = [cell.strip() for cell in line.strip('|').split('|')]
                table_rows.append(cells)
                processed_lines[i] = True
            elif in_table:
                # End of table
                table = TableElement(rows=table_rows)
                elements_with_position.append({
                    'position': table_start_line,
                    'element': table.to_dict()
                })
                table_rows = []
                in_table = False
        
        # Handle table at the end of the document
        if in_table and table_rows:
            table = TableElement(rows=table_rows)
            elements_with_position.append({
                'position': table_start_line,
                'element': table.to_dict()
            })
    
    def parse_unordered_lists(self, lines: List[str], 
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
        in_list = False
        
        for i, line in enumerate(lines):
            if processed_lines[i]:
                # Skip already processed lines
                if in_list and list_items:
                    # End of list
                    list_element = ListElement(
                        items=list_items,
                        list_type='unordered'
                    )
                    elements_with_position.append({
                        'position': list_start_line,
                        'element': list_element.to_dict()
                    })
                    list_items = []
                    in_list = False
                continue
            
            line = line.strip()
            if line.startswith('=>'):
                # This is an unordered list item
                if not in_list:
                    list_start_line = i
                    in_list = True
                
                # Extract the item text
                item_text = line[2:].strip()
                
                # Extract inline styles and class/id
                item_text, attributes = self.extract_inline_attributes(item_text)
                
                # Process links and images
                inline_elements = self.process_inline_elements(item_text)
                for element in inline_elements:
                    if element['type'] == 'link':
                        link_element = LinkElement(
                            content=element['element']['content'],
                            href=element['element']['href']
                        )
                        item_text = item_text.replace(element['original'], link_element.to_html())
                    elif element['type'] == 'image':
                        image_element = ImageElement(
                            alt=element['element']['alt'],
                            src=element['element']['src']
                        )
                        item_text = item_text.replace(element['original'], image_element.to_html())
                
                # Create the list item
                list_item = ListItemElement(
                    content=item_text,
                    list_type='unordered',
                    attributes=attributes
                )
                
                list_items.append(list_item.to_dict())
                processed_lines[i] = True
            elif in_list and not line:
                # Empty line after list items - could be a continuation or end of list
                # For now, we'll treat it as a continuation
                processed_lines[i] = True
            elif in_list:
                # End of list
                list_element = ListElement(
                    items=list_items,
                    list_type='unordered'
                )
                elements_with_position.append({
                    'position': list_start_line,
                    'element': list_element.to_dict()
                })
                list_items = []
                in_list = False
        
        # Handle list at the end of the document
        if in_list and list_items:
            list_element = ListElement(
                items=list_items,
                list_type='unordered'
            )
            elements_with_position.append({
                'position': list_start_line,
                'element': list_element.to_dict()
            })
    
    def parse_ordered_lists(self, lines: List[str], 
                           processed_lines: List[bool], 
                           elements_with_position: List[Dict[str, Any]]) -> None:
        """Parse ordered list elements from the content.
        
        Args:
            lines: Content split into lines
            processed_lines: Tracking which lines have been processed
            elements_with_position: List to append parsed elements with their positions
        """
        list_items = []
        list_start_line = -1
        in_list = False
        
        for i, line in enumerate(lines):
            if processed_lines[i]:
                # Skip already processed lines
                if in_list and list_items:
                    # End of list
                    list_element = ListElement(
                        items=list_items,
                        list_type='ordered'
                    )
                    elements_with_position.append({
                        'position': list_start_line,
                        'element': list_element.to_dict()
                    })
                    list_items = []
                    in_list = False
                continue
            
            line = line.strip()
            ordered_list_match = re.match(r'^(\d+)\.\s+(.+)$', line)
            if ordered_list_match:
                # This is an ordered list item
                if not in_list:
                    list_start_line = i
                    in_list = True
                
                # Extract the item text and index
                list_index = int(ordered_list_match.group(1))
                item_text = ordered_list_match.group(2).strip()
                
                # Extract inline styles and class/id
                item_text, attributes = self.extract_inline_attributes(item_text)
                
                # Process links and images
                inline_elements = self.process_inline_elements(item_text)
                for element in inline_elements:
                    if element['type'] == 'link':
                        link_element = LinkElement(
                            content=element['element']['content'],
                            href=element['element']['href']
                        )
                        item_text = item_text.replace(element['original'], link_element.to_html())
                    elif element['type'] == 'image':
                        image_element = ImageElement(
                            alt=element['element']['alt'],
                            src=element['element']['src']
                        )
                        item_text = item_text.replace(element['original'], image_element.to_html())
                
                # Create the list item
                list_item = ListItemElement(
                    content=item_text,
                    list_type='ordered',
                    list_index=list_index,
                    attributes=attributes
                )
                
                list_items.append(list_item.to_dict())
                processed_lines[i] = True
            elif in_list and not line:
                # Empty line after list items - could be a continuation or end of list
                # For now, we'll treat it as a continuation
                processed_lines[i] = True
            elif in_list:
                # End of list
                list_element = ListElement(
                    items=list_items,
                    list_type='ordered'
                )
                elements_with_position.append({
                    'position': list_start_line,
                    'element': list_element.to_dict()
                })
                list_items = []
                in_list = False
        
        # Handle list at the end of the document
        if in_list and list_items:
            list_element = ListElement(
                items=list_items,
                list_type='ordered'
            )
            elements_with_position.append({
                'position': list_start_line,
                'element': list_element.to_dict()
            })
    
    def parse_paragraphs(self, lines: List[str], 
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
        in_paragraph = False
        
        for i, line in enumerate(lines):
            if processed_lines[i]:
                # Skip already processed lines
                if in_paragraph and paragraph_lines:
                    # End of paragraph
                    paragraph_text = ' '.join(paragraph_lines)
                    
                    # Process links and images
                    inline_elements = self.process_inline_elements(paragraph_text)
                    for element in inline_elements:
                        if element['type'] == 'link':
                            link_element = LinkElement(
                                content=element['element']['content'],
                                href=element['element']['href']
                            )
                            paragraph_text = paragraph_text.replace(element['original'], link_element.to_html())
                        elif element['type'] == 'image':
                            image_element = ImageElement(
                                alt=element['element']['alt'],
                                src=element['element']['src']
                            )
                            paragraph_text = paragraph_text.replace(element['original'], image_element.to_html())
                    
                    # Create the paragraph element
                    paragraph = ParagraphElement(content=paragraph_text)
                    elements_with_position.append({
                        'position': paragraph_start_line,
                        'element': paragraph.to_dict()
                    })
                    paragraph_lines = []
                    in_paragraph = False
                continue
            
            line = line.strip()
            if line and not in_paragraph:
                # Start of a new paragraph
                paragraph_start_line = i
                in_paragraph = True
                paragraph_lines.append(line)
                processed_lines[i] = True
            elif line and in_paragraph:
                # Continuation of paragraph
                paragraph_lines.append(line)
                processed_lines[i] = True
            elif not line and in_paragraph:
                # End of paragraph
                paragraph_text = ' '.join(paragraph_lines)
                
                # Process links and images
                inline_elements = self.process_inline_elements(paragraph_text)
                for element in inline_elements:
                    if element['type'] == 'link':
                        link_element = LinkElement(
                            content=element['element']['content'],
                            href=element['element']['href']
                        )
                        paragraph_text = paragraph_text.replace(element['original'], link_element.to_html())
                    elif element['type'] == 'image':
                        image_element = ImageElement(
                            alt=element['element']['alt'],
                            src=element['element']['src']
                        )
                        paragraph_text = paragraph_text.replace(element['original'], image_element.to_html())
                
                # Create the paragraph element
                paragraph = ParagraphElement(content=paragraph_text)
                elements_with_position.append({
                    'position': paragraph_start_line,
                    'element': paragraph.to_dict()
                })
                paragraph_lines = []
                in_paragraph = False
                processed_lines[i] = True
        
        # Handle paragraph at the end of the document
        if in_paragraph and paragraph_lines:
            paragraph_text = ' '.join(paragraph_lines)
            
            # Process links and images
            inline_elements = self.process_inline_elements(paragraph_text)
            for element in inline_elements:
                if element['type'] == 'link':
                    link_element = LinkElement(
                        content=element['element']['content'],
                        href=element['element']['href']
                    )
                    paragraph_text = paragraph_text.replace(element['original'], link_element.to_html())
                elif element['type'] == 'image':
                    image_element = ImageElement(
                        alt=element['element']['alt'],
                        src=element['element']['src']
                    )
                    paragraph_text = paragraph_text.replace(element['original'], image_element.to_html())
            
            # Create the paragraph element
            paragraph = ParagraphElement(content=paragraph_text)
            elements_with_position.append({
                'position': paragraph_start_line,
                'element': paragraph.to_dict()
            })
