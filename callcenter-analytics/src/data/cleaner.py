"""
Data Cleaner Module
Handles data cleaning, missing value treatment, and outlier detection
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional


class DataCleaner:
    """Clean and preprocess KPI data"""

    def __init__(self, config: dict):
        self.config = config
        self.outlier_std = config.get('analysis', {}).get('outlier_std', 3)

    def handle_missing_values(self, df: pd.DataFrame, strategy: str = 'auto') -> pd.DataFrame:
        """
        Handle missing values in DataFrame

        Args:
            df: Input DataFrame
            strategy: 'auto', 'drop', 'mean', 'median', 'forward_fill'

        Returns:
            DataFrame with missing values handled
        """
        df_copy = df.copy()
        missing_report = df_copy.isnull().sum()

        if missing_report.sum() == 0:
            print("✓ No missing values found")
            return df_copy

        print(f"\n📊 Missing Values Report:")
        print(missing_report[missing_report > 0])

        if strategy == 'drop':
            df_copy = df_copy.dropna()
            print(f"✓ Dropped rows with missing values. Remaining: {len(df_copy)} rows")

        elif strategy == 'mean':
            numeric_cols = df_copy.select_dtypes(include=[np.number]).columns
            df_copy[numeric_cols] = df_copy[numeric_cols].fillna(df_copy[numeric_cols].mean())
            print("✓ Filled numeric columns with mean values")

        elif strategy == 'median':
            numeric_cols = df_copy.select_dtypes(include=[np.number]).columns
            df_copy[numeric_cols] = df_copy[numeric_cols].fillna(df_copy[numeric_cols].median())
            print("✓ Filled numeric columns with median values")

        elif strategy == 'forward_fill':
            df_copy = df_copy.fillna(method='ffill')
            print("✓ Forward filled missing values")

        elif strategy == 'auto':
            numeric_cols = df_copy.select_dtypes(include=[np.number]).columns
            df_copy[numeric_cols] = df_copy[numeric_cols].fillna(df_copy[numeric_cols].median())

            categorical_cols = df_copy.select_dtypes(include=['object']).columns
            df_copy[categorical_cols] = df_copy[categorical_cols].fillna('Unknown')
            print("✓ Auto-filled: numeric with median, categorical with 'Unknown'")

        return df_copy

    def detect_outliers(self, df: pd.DataFrame, columns: Optional[List[str]] = None) -> Dict[str, pd.Series]:
        """
        Detect outliers using z-score method

        Args:
            df: Input DataFrame
            columns: Columns to check (all numeric if None)

        Returns:
            Dictionary mapping column names to boolean Series (True = outlier)
        """
        if columns is None:
            columns = df.select_dtypes(include=[np.number]).columns.tolist()

        outliers = {}
        for col in columns:
            if col in df.columns and pd.api.types.is_numeric_dtype(df[col]):
                z_scores = np.abs((df[col] - df[col].mean()) / df[col].std())
                outliers[col] = z_scores > self.outlier_std
                outlier_count = outliers[col].sum()
                if outlier_count > 0:
                    print(f"⚠ {col}: {outlier_count} outliers detected")

        return outliers

    def remove_outliers(self, df: pd.DataFrame, columns: Optional[List[str]] = None) -> pd.DataFrame:
        """
        Remove outliers from DataFrame

        Args:
            df: Input DataFrame
            columns: Columns to check (all numeric if None)

        Returns:
            DataFrame with outliers removed
        """
        outliers = self.detect_outliers(df, columns)

        mask = pd.Series([True] * len(df), index=df.index)
        for col, outlier_mask in outliers.items():
            mask &= ~outlier_mask

        df_clean = df[mask].copy()
        removed = len(df) - len(df_clean)
        print(f"✓ Removed {removed} rows with outliers. Remaining: {len(df_clean)} rows")

        return df_clean

    def remove_duplicates(self, df: pd.DataFrame, subset: Optional[List[str]] = None) -> pd.DataFrame:
        """
        Remove duplicate rows

        Args:
            df: Input DataFrame
            subset: Columns to consider for duplicates (all if None)

        Returns:
            DataFrame without duplicates
        """
        initial_count = len(df)
        df_clean = df.drop_duplicates(subset=subset)
        removed = initial_count - len(df_clean)

        if removed > 0:
            print(f"✓ Removed {removed} duplicate rows")
        else:
            print("✓ No duplicates found")

        return df_clean

    def standardize_column_names(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Standardize column names (lowercase, replace spaces with underscores)

        Args:
            df: Input DataFrame

        Returns:
            DataFrame with standardized column names
        """
        df_copy = df.copy()
        df_copy.columns = df_copy.columns.str.lower().str.replace(' ', '_').str.replace('-', '_')
        print("✓ Standardized column names")
        return df_copy

    def clean_data(self, df: pd.DataFrame, remove_outliers: bool = False) -> pd.DataFrame:
        """
        Complete data cleaning pipeline

        Args:
            df: Input DataFrame
            remove_outliers: Whether to remove outliers

        Returns:
            Cleaned DataFrame
        """
        print("\n🧹 Starting data cleaning...")

        df_clean = self.standardize_column_names(df)
        df_clean = self.remove_duplicates(df_clean)
        df_clean = self.handle_missing_values(df_clean, strategy='auto')

        if remove_outliers:
            df_clean = self.remove_outliers(df_clean)

        print("\n✓ Data cleaning completed")
        return df_clean
