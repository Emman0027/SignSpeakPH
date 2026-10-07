import os
import sys

import pytest

# Add the root directory to the path so we can import modules like app
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
