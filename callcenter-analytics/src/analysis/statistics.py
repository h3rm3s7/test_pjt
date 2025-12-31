"""
Statistical Analyzer Module
Perform statistical tests and analysis
"""

import pandas as pd
import numpy as np
from scipy import stats
from typing import Dict, List, Tuple, Optional


class StatisticalAnalyzer:
    """Perform statistical analysis on KPI data"""

    def __init__(self, config: dict):
        self.config = config

    def descriptive_statistics(self, df: pd.DataFrame) -> Dict[str, pd.DataFrame]:
        """
        Calculate descriptive statistics

        Args:
            df: Input DataFrame

        Returns:
            Dictionary with statistics for numeric and categorical columns
        """
        results = {}

        # Numeric columns
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) > 0:
            results['numeric'] = df[numeric_cols].describe()

        # Categorical columns
        categorical_cols = df.select_dtypes(include=['object']).columns
        if len(categorical_cols) > 0:
            cat_stats = []
            for col in categorical_cols:
                cat_stats.append({
                    'column': col,
                    'unique_values': df[col].nunique(),
                    'most_common': df[col].mode()[0] if len(df[col].mode()) > 0 else None,
                    'most_common_freq': df[col].value_counts().iloc[0] if len(df[col]) > 0 else 0
                })
            results['categorical'] = pd.DataFrame(cat_stats)

        print("\n📊 Descriptive Statistics:")
        if 'numeric' in results:
            print(f"  Numeric columns: {len(numeric_cols)}")
        if 'categorical' in results:
            print(f"  Categorical columns: {len(categorical_cols)}")

        return results

    def test_normality(self, df: pd.DataFrame, columns: Optional[List[str]] = None) -> Dict[str, Dict]:
        """
        Test for normality using Shapiro-Wilk test

        Args:
            df: Input DataFrame
            columns: Columns to test (all numeric if None)

        Returns:
            Dictionary with test results
        """
        if columns is None:
            columns = df.select_dtypes(include=[np.number]).columns.tolist()

        results = {}

        for col in columns:
            if col in df.columns and len(df[col].dropna()) > 3:
                data = df[col].dropna()

                # Sample if too large (Shapiro-Wilk works best with n < 5000)
                if len(data) > 5000:
                    data = data.sample(5000, random_state=42)

                statistic, p_value = stats.shapiro(data)

                results[col] = {
                    'statistic': statistic,
                    'p_value': p_value,
                    'is_normal': p_value > 0.05  # 5% significance level
                }

        print("\n🔬 Normality Tests (Shapiro-Wilk):")
        for col, result in results.items():
            normal_str = "Normal" if result['is_normal'] else "Not Normal"
            print(f"  {col}: {normal_str} (p={result['p_value']:.4f})")

        return results

    def perform_t_test(self, group1: pd.Series, group2: pd.Series) -> Dict[str, float]:
        """
        Perform independent t-test

        Args:
            group1: First group data
            group2: Second group data

        Returns:
            Dictionary with test results
        """
        statistic, p_value = stats.ttest_ind(group1.dropna(), group2.dropna())

        result = {
            'statistic': statistic,
            'p_value': p_value,
            'significant': p_value < 0.05,
            'group1_mean': group1.mean(),
            'group2_mean': group2.mean(),
            'mean_difference': group1.mean() - group2.mean()
        }

        print(f"\n📊 T-Test Results:")
        print(f"  Statistic: {result['statistic']:.4f}")
        print(f"  P-value: {result['p_value']:.4f}")
        print(f"  Significant: {result['significant']}")

        return result

    def calculate_confidence_interval(self, data: pd.Series, confidence: float = 0.95) -> Tuple[float, float, float]:
        """
        Calculate confidence interval for mean

        Args:
            data: Input data series
            confidence: Confidence level (default 0.95 for 95%)

        Returns:
            Tuple of (mean, lower_bound, upper_bound)
        """
        data_clean = data.dropna()
        mean = data_clean.mean()
        sem = stats.sem(data_clean)
        interval = sem * stats.t.ppf((1 + confidence) / 2, len(data_clean) - 1)

        return mean, mean - interval, mean + interval

    def detect_anomalies(self, df: pd.DataFrame, column: str, method: str = 'zscore',
                        threshold: float = 3.0) -> pd.DataFrame:
        """
        Detect anomalies in a column

        Args:
            df: Input DataFrame
            column: Column to analyze
            method: 'zscore' or 'iqr'
            threshold: Threshold for anomaly detection

        Returns:
            DataFrame with anomaly flags
        """
        df_copy = df.copy()

        if method == 'zscore':
            z_scores = np.abs(stats.zscore(df_copy[column].dropna()))
            df_copy['is_anomaly'] = z_scores > threshold

        elif method == 'iqr':
            Q1 = df_copy[column].quantile(0.25)
            Q3 = df_copy[column].quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - threshold * IQR
            upper_bound = Q3 + threshold * IQR
            df_copy['is_anomaly'] = (df_copy[column] < lower_bound) | (df_copy[column] > upper_bound)

        anomaly_count = df_copy['is_anomaly'].sum()
        print(f"\n🚨 Anomaly Detection ({method}):")
        print(f"  Column: {column}")
        print(f"  Anomalies found: {anomaly_count} ({anomaly_count/len(df_copy)*100:.2f}%)")

        return df_copy

    def time_series_decomposition(self, df: pd.DataFrame, date_column: str,
                                  value_column: str, period: int = 7) -> Dict[str, pd.Series]:
        """
        Decompose time series into trend, seasonal, and residual components

        Args:
            df: Input DataFrame
            date_column: Date column name
            value_column: Value column name
            period: Seasonal period

        Returns:
            Dictionary with decomposition components
        """
        from statsmodels.tsa.seasonal import seasonal_decompose

        df_ts = df.copy()
        df_ts[date_column] = pd.to_datetime(df_ts[date_column])
        df_ts = df_ts.set_index(date_column).sort_index()

        # Ensure regular frequency
        df_ts = df_ts[value_column].resample('D').mean().fillna(method='ffill')

        # Decomposition
        decomposition = seasonal_decompose(df_ts, model='additive', period=period)

        results = {
            'trend': decomposition.trend,
            'seasonal': decomposition.seasonal,
            'residual': decomposition.resid,
            'observed': decomposition.observed
        }

        print(f"\n📈 Time Series Decomposition:")
        print(f"  Period: {period}")
        print(f"  Components: trend, seasonal, residual")

        return results

    def compare_distributions(self, group1: pd.Series, group2: pd.Series) -> Dict[str, any]:
        """
        Compare two distributions using various statistical tests

        Args:
            group1: First group data
            group2: Second group data

        Returns:
            Dictionary with comparison results
        """
        results = {}

        # Kolmogorov-Smirnov test
        ks_stat, ks_p = stats.ks_2samp(group1.dropna(), group2.dropna())
        results['ks_test'] = {
            'statistic': ks_stat,
            'p_value': ks_p,
            'different_distributions': ks_p < 0.05
        }

        # Mann-Whitney U test (non-parametric)
        u_stat, u_p = stats.mannwhitneyu(group1.dropna(), group2.dropna())
        results['mann_whitney'] = {
            'statistic': u_stat,
            'p_value': u_p,
            'significant_difference': u_p < 0.05
        }

        print(f"\n🔬 Distribution Comparison:")
        print(f"  KS Test p-value: {ks_p:.4f}")
        print(f"  Mann-Whitney p-value: {u_p:.4f}")

        return results

    def analyze_variance(self, df: pd.DataFrame, value_column: str, group_column: str) -> Dict[str, any]:
        """
        Perform ANOVA to compare means across multiple groups

        Args:
            df: Input DataFrame
            value_column: Column with values to compare
            group_column: Column with group labels

        Returns:
            Dictionary with ANOVA results
        """
        groups = [group[value_column].dropna() for name, group in df.groupby(group_column)]

        # Perform one-way ANOVA
        f_stat, p_value = stats.f_oneway(*groups)

        results = {
            'f_statistic': f_stat,
            'p_value': p_value,
            'significant': p_value < 0.05,
            'num_groups': len(groups),
            'group_means': df.groupby(group_column)[value_column].mean().to_dict()
        }

        print(f"\n📊 ANOVA Results:")
        print(f"  F-statistic: {f_stat:.4f}")
        print(f"  P-value: {p_value:.4f}")
        print(f"  Significant difference: {results['significant']}")

        return results
