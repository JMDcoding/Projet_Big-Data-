"""
Initialization for storage module.
"""
from src.storage.data_lake import DataLake, JSONDataLake, CSVDataLake

__all__ = [
    "DataLake",
    "JSONDataLake",
    "CSVDataLake",
]
