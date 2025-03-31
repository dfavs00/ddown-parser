#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Main entry point for the ddown_parser package when run as a module.

This allows the package to be run with `python -m ddown_parser`.
"""

import sys
from typing import List, Optional

from .cli import main


if __name__ == "__main__":
    sys.exit(main())
