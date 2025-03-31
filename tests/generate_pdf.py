#!/usr/bin/env python
"""
Simple script to test PDF generation from a Ddown file.

This script demonstrates how to use the Ddown parser to convert a Ddown file to PDF.
"""

import argparse
import os
import sys
from pathlib import Path

# Add the parent directory to the path so we can import the ddown_parser module
sys.path.insert(0, str(Path(__file__).parent.parent))

from ddown_parser import DdownParser


def parse_arguments() -> argparse.Namespace:
    """Parse command-line arguments.
    
    Returns:
        Parsed arguments
    """
    parser = argparse.ArgumentParser(description="Convert a Ddown file to PDF")
    parser.add_argument(
        "input", 
        help="Path to the input Ddown file"
    )
    parser.add_argument(
        "-o", "--output",
        help="Path to the output PDF file (default: input filename with .pdf extension)"
    )
    return parser.parse_args()


def main() -> None:
    """Main function to convert a Ddown file to PDF."""
    args = parse_arguments()
    
    # Get the input and output file paths
    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Error: Input file '{input_path}' does not exist.")
        sys.exit(1)
    
    # If no output path is specified, use the input filename with .pdf extension
    if args.output:
        output_path = Path(args.output)
    else:
        output_path = input_path.with_suffix(".pdf")
    
    # Create the parser and convert the file
    try:
        parser = DdownParser()
        print(f"Converting {input_path} to PDF...")
        pdf_bytes = parser.parse_file(str(input_path), output_format="pdf")
        
        # Write the PDF to the output file
        with open(output_path, "wb") as f:
            f.write(pdf_bytes)
        
        print(f"Successfully converted {input_path} to {output_path}")
    except ImportError as e:
        print(f"Error: {e}")
        print("Please install the required dependencies:")
        print("  pip install weasyprint")
        print("  or")
        print("  pip install pdfkit")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
