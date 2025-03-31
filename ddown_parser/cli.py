import argparse
import sys
from pathlib import Path
from typing import List, Optional, Union

from .parser import DdownParser


def parse_arguments(args: Optional[List[str]] = None) -> argparse.Namespace:
    """Parse command line arguments.
    
    Args:
        args: Command line arguments (defaults to sys.argv[1:] if None)
        
    Returns:
        Parsed arguments namespace
    """
    parser = argparse.ArgumentParser(
        description="Convert Ddown files to various output formats",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    parser.add_argument(
        "input_file",
        type=str,
        help="Path to the input Ddown file"
    )
    
    parser.add_argument(
        "-f", "--format",
        type=str,
        choices=["html", "pdf"],
        default="html",
        help="Output format"
    )
    
    parser.add_argument(
        "-o", "--output",
        type=str,
        help="Output file path (defaults to input filename with appropriate extension)"
    )
    
    parser.add_argument(
        "--css",
        type=str,
        help="Path to a custom CSS file to use for styling the output"
    )
    
    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s 0.1.0"
    )
    
    return parser.parse_args(args)


def get_default_output_path(input_path: Union[str, Path], output_format: str) -> Path:
    """Generate default output path based on input path and format.
    
    Args:
        input_path: Path to the input file
        output_format: Desired output format
        
    Returns:
        Default output path with appropriate extension
    """
    input_path = Path(input_path) if isinstance(input_path, str) else input_path
    return input_path.with_suffix(f".{output_format}")


def main(args: Optional[List[str]] = None) -> int:
    """Main entry point for the CLI.
    
    Args:
        args: Command line arguments (defaults to sys.argv[1:] if None)
        
    Returns:
        Exit code (0 for success, non-zero for errors)
    """
    try:
        # Parse command line arguments
        parsed_args = parse_arguments(args)
        
        # Check if input file exists
        input_path = Path(parsed_args.input_file)
        if not input_path.exists():
            print(f"Error: Input file '{input_path}' does not exist.", file=sys.stderr)
            return 1
        
        # Check if custom CSS file exists if specified
        custom_css = None
        if parsed_args.css:
            css_path = Path(parsed_args.css)
            if not css_path.exists():
                print(f"Error: CSS file '{css_path}' does not exist.", file=sys.stderr)
                return 1
            with open(css_path, 'r', encoding='utf-8') as f:
                custom_css = f.read()
        
        # Create parser instance
        parser = DdownParser()
        
        # Determine output path
        output_path = parsed_args.output
        if not output_path:
            output_path = get_default_output_path(parsed_args.input_file, parsed_args.format)
        else:
            output_path = Path(output_path)
        
        # Create output directory if it doesn't exist
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            # Parse the input file
            result = parser.parse_file(parsed_args.input_file, output_format=parsed_args.format, custom_css=custom_css)
            
            # Write the result to the output file
            mode = "wb" if isinstance(result, bytes) else "w"
            with open(output_path, mode) as f:
                f.write(result)
            
            print(f"Successfully converted {parsed_args.input_file} to {output_path}")
            return 0
            
        except ImportError as e:
            if parsed_args.format == "pdf":
                print(f"Error: {e}", file=sys.stderr)
                print("To generate PDFs, you need to install one of the following:", file=sys.stderr)
                print("  pip install weasyprint", file=sys.stderr)
                print("  or", file=sys.stderr)
                print("  pip install pdfkit", file=sys.stderr)
                return 1
            raise
    
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
