"""
Package initialization.
"""
from src.ingestion import *
from src.storage import *
from src.transformation import *
from src.visualization import *
from src.utils import *

# Optional database module (requires psycopg2)
try:
    from src.database import *
except ImportError:
    import warnings
    warnings.warn("Database module not available. Install psycopg2-binary: pip install psycopg2-binary")

__version__ = "1.0.0"
__author__ = "Big Data Team"
