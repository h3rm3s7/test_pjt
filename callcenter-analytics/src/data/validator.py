"""
Data Validator Module
Validates data quality and schema requirements
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple


class DataValidator:
    """Validate KPI data quality and schema"""

    def __init__(self, config: dict):
        self.config = config
        self.min_data_points = config.get('analysis', {}).get('min_data_points', 30)

    def validate_schema(self, df: pd.DataFrame, required_columns: List[str]) -> Tuple[bool, List[str]]:
        """
        Validate that required columns exist

        Args:
            df: Input DataFrame
            required_columns: List of required column names

        Returns:
            Tuple of (is_valid, missing_columns)
        """
        missing = [col for col in required_columns if col not in df.columns]
        is_valid = len(missing) == 0

        if is_valid:
            print("✓ All required columns present")
        else:
            print(f"✗ Missing columns: {missing}")

        return is_valid, missing

    def validate_data_types(self, df: pd.DataFrame, type_spec: Dict[str, str]) -> Tuple[bool, Dict[str, str]]:
        """
        Validate column data types

        Args:
            df: Input DataFrame
            type_spec: Dictionary mapping column names to expected types
                      ('numeric', 'string', 'datetime', 'boolean')

        Returns:
            Tuple of (is_valid, type_mismatches)
        """
        mismatches = {}

        for col, expected_type in type_spec.items():
            if col not in df.columns:
                continue

            actual_dtype = df[col].dtype
            is_valid = False

            if expected_type == 'numeric':
                is_valid = pd.api.types.is_numeric_dtype(actual_dtype)
            elif expected_type == 'string':
                is_valid = pd.api.types.is_string_dtype(actual_dtype) or actual_dtype == 'object'
            elif expected_type == 'datetime':
                is_valid = pd.api.types.is_datetime64_any_dtype(actual_dtype)
            elif expected_type == 'boolean':
                is_valid = pd.api.types.is_bool_dtype(actual_dtype)

            if not is_valid:
                mismatches[col] = f"Expected {expected_type}, got {actual_dtype}"

        if not mismatches:
            print("✓ All data types valid")
        else:
            print(f"✗ Type mismatches: {mismatches}")

        return len(mismatches) == 0, mismatches

    def validate_value_ranges(self, df: pd.DataFrame, range_spec: Dict[str, Tuple[float, float]]) -> Tuple[bool, Dict[str, int]]:
        """
        Validate that numeric values are within expected ranges

        Args:
            df: Input DataFrame
            range_spec: Dictionary mapping column names to (min, max) tuples

        Returns:
            Tuple of (is_valid, violations_count)
        """
        violations = {}

        for col, (min_val, max_val) in range_spec.items():
            if col not in df.columns:
                continue

            out_of_range = ((df[col] < min_val) | (df[col] > max_val)).sum()
            if out_of_range > 0:
                violations[col] = out_of_range

        if not violations:
            print("✓ All values within expected ranges")
        else:
            print(f"✗ Range violations: {violations}")

        return len(violations) == 0, violations

    def check_data_quality(self, df: pd.DataFrame) -> Dict[str, any]:
        """
        Generate comprehensive data quality report

        Args:
            df: Input DataFrame

        Returns:
            Dictionary with quality metrics
        """
        report = {
            'total_rows': len(df),
            'total_columns': len(df.columns),
            'missing_values': df.isnull().sum().to_dict(),
            'missing_percentage': (df.isnull().sum() / len(df) * 100).to_dict(),
            'duplicate_rows': df.duplicated().sum(),
            'numeric_columns': df.select_dtypes(include=[np.number]).columns.tolist(),
            'categorical_columns': df.select_dtypes(include=['object']).columns.tolist(),
        }

        # Add statistics for numeric columns
        numeric_stats = {}
        for col in report['numeric_columns']:
            numeric_stats[col] = {
                'mean': df[col].mean(),
                'median': df[col].median(),
                'std': df[col].std(),
                'min': df[col].min(),
                'max': df[col].max(),
            }
        report['numeric_stats'] = numeric_stats

        print("\n📊 Data Quality Report:")
        print(f"  Total rows: {report['total_rows']}")
        print(f"  Total columns: {report['total_columns']}")
        print(f"  Duplicate rows: {report['duplicate_rows']}")
        print(f"  Numeric columns: {len(report['numeric_columns'])}")
        print(f"  Categorical columns: {len(report['categorical_columns'])}")

        return report

    def validate_sufficient_data(self, df: pd.DataFrame) -> Tuple[bool, str]:
        """
        Validate that there is sufficient data for analysis

        Args:
            df: Input DataFrame

        Returns:
            Tuple of (is_valid, message)
        """
        row_count = len(df)

        if row_count < self.min_data_points:
            message = f"Insufficient data: {row_count} rows (minimum: {self.min_data_points})"
            print(f"✗ {message}")
            return False, message

        message = f"Sufficient data: {row_count} rows"
        print(f"✓ {message}")
        return True, message

    def validate_all(self, df: pd.DataFrame, required_columns: List[str] = None) -> Dict[str, any]:
        """
        Run all validations

        Args:
            df: Input DataFrame
            required_columns: Optional list of required columns

        Returns:
            Dictionary with validation results
        """
        print("\n🔍 Validating data...")

        results = {
            'quality_report': self.check_data_quality(df),
            'sufficient_data': self.validate_sufficient_data(df),
        }

        if required_columns:
            results['schema_valid'] = self.validate_schema(df, required_columns)

        print("\n✓ Validation completed")
        return results
