"""
Data Loader Module
Handles loading CSV files and basic data import operations
"""

import pandas as pd
import os
from typing import Optional, List
from pathlib import Path


class DataLoader:
    """Load and import KPI data from various sources"""

    def __init__(self, config: dict):
        self.config = config
        self.encoding = config.get('data', {}).get('encoding', 'utf-8')
        self.date_format = config.get('data', {}).get('date_format', '%Y-%m-%d')

    def load_csv(self, file_path: str, **kwargs) -> pd.DataFrame:
        """
        Load CSV file into DataFrame

        Args:
            file_path: Path to CSV file
            **kwargs: Additional arguments for pd.read_csv

        Returns:
            DataFrame with loaded data
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        try:
            df = pd.read_csv(file_path, encoding=self.encoding, **kwargs)
            print(f"✓ Loaded {len(df)} rows from {file_path}")
            return df
        except Exception as e:
            raise Exception(f"Error loading CSV: {str(e)}")

    def load_multiple_csv(self, file_paths: List[str]) -> pd.DataFrame:
        """
        Load and concatenate multiple CSV files

        Args:
            file_paths: List of CSV file paths

        Returns:
            Combined DataFrame
        """
        dfs = []
        for path in file_paths:
            df = self.load_csv(path)
            dfs.append(df)

        combined_df = pd.concat(dfs, ignore_index=True)
        print(f"✓ Combined {len(dfs)} files into {len(combined_df)} rows")
        return combined_df

    def load_from_directory(self, directory: str, pattern: str = "*.csv") -> pd.DataFrame:
        """
        Load all CSV files from a directory

        Args:
            directory: Directory path
            pattern: File pattern (default: *.csv)

        Returns:
            Combined DataFrame
        """
        path = Path(directory)
        csv_files = list(path.glob(pattern))

        if not csv_files:
            raise FileNotFoundError(f"No files matching '{pattern}' found in {directory}")

        file_paths = [str(f) for f in csv_files]
        return self.load_multiple_csv(file_paths)

    def detect_date_columns(self, df: pd.DataFrame) -> List[str]:
        """
        Auto-detect date columns in DataFrame

        Args:
            df: Input DataFrame

        Returns:
            List of column names that appear to be dates
        """
        date_columns = []
        for col in df.columns:
            if 'date' in col.lower() or 'time' in col.lower():
                date_columns.append(col)
        return date_columns

    def parse_dates(self, df: pd.DataFrame, date_columns: Optional[List[str]] = None) -> pd.DataFrame:
        """
        Parse date columns to datetime type

        Args:
            df: Input DataFrame
            date_columns: List of date columns (auto-detect if None)

        Returns:
            DataFrame with parsed dates
        """
        if date_columns is None:
            date_columns = self.detect_date_columns(df)

        df_copy = df.copy()
        for col in date_columns:
            if col in df_copy.columns:
                try:
                    df_copy[col] = pd.to_datetime(df_copy[col], format=self.date_format, errors='coerce')
                    print(f"✓ Parsed date column: {col}")
                except Exception as e:
                    print(f"⚠ Failed to parse {col}: {str(e)}")

        return df_copy
