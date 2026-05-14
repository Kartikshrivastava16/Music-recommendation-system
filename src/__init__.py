"""
Music Recommendation System - ML-based song recommendation engine
"""

__version__ = "1.0.0"
__author__ = "Your Name"

import sys
from pathlib import Path

# Add src directory to path
src_path = Path(__file__).parent
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))
