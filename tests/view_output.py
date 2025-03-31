from ddown_parser import DdownParser

# Parse the example file and print the HTML output
parser = DdownParser()
html_output = parser.parse_file('examples/simple.ddown', output_format='html')
print(html_output)
