# Ddown Parser

A Python-based parser for converting Ddown files (.ddown) to various output formats including HTML, PDF, and more.

## What is Ddown?

Ddown is a custom markdown-like language with unique syntax features including:

- Heading levels defined by different underline characters
- Unordered lists using the "=> " prefix
- Styling capabilities with global and inline CSS
- Class and ID assignments for elements
- Support for standard markdown elements like code blocks, quotes, images, and links

## Features

- Parse Ddown files to an intermediate representation
- Convert Ddown to HTML with CSS styling
- Generate PDF documents from Ddown
- Support for all Ddown syntax elements

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/ddown-parser.git
cd ddown-parser

# Create and activate a virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Usage

```python
from ddown_parser import DdownParser

# Parse a Ddown file to HTML
parser = DdownParser()
html_output = parser.parse_file('example.ddown', output_format='html')

# Save the output
with open('output.html', 'w') as f:
    f.write(html_output)

# Generate PDF
pdf_output = parser.parse_file('example.ddown', output_format='pdf')
with open('output.pdf', 'wb') as f:
    f.write(pdf_output)
```

## Command Line Interface

```bash
# Convert to HTML
python -m ddown_parser example.ddown --format html --output output.html

# Convert to PDF
python -m ddown_parser example.ddown --format pdf --output output.pdf
```

## Development

```bash
# Run tests
python -m pytest

# Check code style
python -m flake8
```

## License

MIT
