from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="ddown-parser",
    version="0.1.0",
    author="Dom",
    author_email="dom@favata.com",
    description="A parser for the Ddown markdown-like language",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/ddown-parser",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    install_requires=[
        "pyyaml>=6.0",
        "markdown>=3.4.0",
        "beautifulsoup4>=4.11.0",
        "weasyprint>=57.0",
    ],
    entry_points={
        "console_scripts": [
            "ddown=ddown_parser.cli:main",
        ],
    },
)
