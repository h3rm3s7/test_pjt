"""
KPI Analyzer Module
Calculate and analyze call center KPI metrics
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional


class KPIAnalyzer:
    """Analyze call center performance and quality KPIs"""

    def __init__(self, config: dict):
        self.config = config
        self.thresholds = config.get('kpi_thresholds', {})

    def calculate_performance_kpis(self, df: pd.DataFrame) -> Dict[str, float]:
        """
        Calculate performance KPIs

        Expected columns:
        - handle_time: Call handle time in seconds
        - first_call_resolution: Binary (1/0 or True/False)
        - calls_offered: Total calls offered
        - calls_answered: Total calls answered
        - answer_time: Time to answer in seconds
        - logged_time: Agent logged in time
        - productive_time: Agent productive time

        Args:
            df: Input DataFrame with performance data

        Returns:
            Dictionary of KPI metrics
        """
        kpis = {}

        # Average Handle Time (AHT)
        if 'handle_time' in df.columns:
            kpis['aht'] = df['handle_time'].mean()
            kpis['aht_median'] = df['handle_time'].median()
            kpis['aht_std'] = df['handle_time'].std()

        # First Call Resolution (FCR)
        if 'first_call_resolution' in df.columns:
            kpis['fcr_rate'] = df['first_call_resolution'].mean()

        # Service Level
        if 'calls_offered' in df.columns and 'calls_answered' in df.columns:
            kpis['service_level'] = (df['calls_answered'].sum() / df['calls_offered'].sum()
                                     if df['calls_offered'].sum() > 0 else 0)

        # Occupancy Rate
        if 'logged_time' in df.columns and 'productive_time' in df.columns:
            total_logged = df['logged_time'].sum()
            total_productive = df['productive_time'].sum()
            kpis['occupancy_rate'] = total_productive / total_logged if total_logged > 0 else 0

        # Adherence (if available)
        if 'scheduled_time' in df.columns and 'actual_time' in df.columns:
            kpis['adherence'] = (df['actual_time'].sum() / df['scheduled_time'].sum()
                                 if df['scheduled_time'].sum() > 0 else 0)

        return kpis

    def calculate_quality_kpis(self, df: pd.DataFrame) -> Dict[str, float]:
        """
        Calculate quality KPIs

        Expected columns:
        - qa_score: Quality assurance score (0-100)
        - csat_score: Customer satisfaction score (1-5)
        - nps_score: Net Promoter Score (-100 to 100)
        - compliance_pass: Binary (1/0 or True/False)
        - error_count: Number of errors
        - total_interactions: Total interactions

        Args:
            df: Input DataFrame with quality data

        Returns:
            Dictionary of quality metrics
        """
        kpis = {}

        # QA Score
        if 'qa_score' in df.columns:
            kpis['qa_score_avg'] = df['qa_score'].mean()
            kpis['qa_score_median'] = df['qa_score'].median()
            kpis['qa_score_std'] = df['qa_score'].std()

        # CSAT Score
        if 'csat_score' in df.columns:
            kpis['csat_avg'] = df['csat_score'].mean()
            kpis['csat_median'] = df['csat_score'].median()

        # NPS Score
        if 'nps_score' in df.columns:
            kpis['nps_avg'] = df['nps_score'].mean()

        # Compliance Rate
        if 'compliance_pass' in df.columns:
            kpis['compliance_rate'] = df['compliance_pass'].mean()

        # Error Rate
        if 'error_count' in df.columns and 'total_interactions' in df.columns:
            total_errors = df['error_count'].sum()
            total_interactions = df['total_interactions'].sum()
            kpis['error_rate'] = total_errors / total_interactions if total_interactions > 0 else 0

        return kpis

    def calculate_all_kpis(self, df: pd.DataFrame) -> Dict[str, Dict[str, float]]:
        """
        Calculate all KPIs

        Args:
            df: Input DataFrame

        Returns:
            Dictionary with 'performance' and 'quality' KPIs
        """
        print("\n📊 Calculating KPIs...")

        results = {
            'performance': self.calculate_performance_kpis(df),
            'quality': self.calculate_quality_kpis(df),
        }

        print(f"  Performance KPIs: {len(results['performance'])} metrics")
        print(f"  Quality KPIs: {len(results['quality'])} metrics")

        return results

    def compare_to_targets(self, kpis: Dict[str, float], kpi_type: str) -> Dict[str, Dict]:
        """
        Compare KPIs to target thresholds

        Args:
            kpis: Calculated KPIs
            kpi_type: 'performance' or 'quality'

        Returns:
            Dictionary with comparison results
        """
        targets = self.thresholds.get(kpi_type, {})
        comparisons = {}

        for kpi_name, value in kpis.items():
            # Map KPI names to target names
            target_key = kpi_name.replace('_avg', '').replace('_rate', '')

            if target_key in targets:
                target = targets[target_key]
                delta = value - target
                pct_delta = (delta / target * 100) if target != 0 else 0

                comparisons[kpi_name] = {
                    'actual': value,
                    'target': target,
                    'delta': delta,
                    'pct_delta': pct_delta,
                    'meets_target': value >= target
                }

        return comparisons

    def generate_kpi_summary(self, kpis: Dict[str, Dict[str, float]]) -> str:
        """
        Generate human-readable KPI summary

        Args:
            kpis: Calculated KPIs

        Returns:
            Summary string
        """
        summary = []
        summary.append("=" * 60)
        summary.append("KPI SUMMARY")
        summary.append("=" * 60)

        # Performance KPIs
        summary.append("\nPERFORMANCE METRICS:")
        for key, value in kpis.get('performance', {}).items():
            if isinstance(value, float):
                summary.append(f"  {key.upper()}: {value:.2f}")

        # Quality KPIs
        summary.append("\nQUALITY METRICS:")
        for key, value in kpis.get('quality', {}).items():
            if isinstance(value, float):
                summary.append(f"  {key.upper()}: {value:.2f}")

        summary.append("=" * 60)

        return "\n".join(summary)

    def analyze_trends(self, df: pd.DataFrame, date_column: str, metric_column: str,
                       period: str = 'D') -> pd.DataFrame:
        """
        Analyze trends over time

        Args:
            df: Input DataFrame
            date_column: Name of date column
            metric_column: Name of metric to analyze
            period: Resampling period ('D'=daily, 'W'=weekly, 'M'=monthly)

        Returns:
            DataFrame with trend analysis
        """
        if date_column not in df.columns or metric_column not in df.columns:
            raise ValueError(f"Columns {date_column} or {metric_column} not found")

        df_trend = df.copy()
        df_trend[date_column] = pd.to_datetime(df_trend[date_column])
        df_trend = df_trend.set_index(date_column)

        trend = df_trend[metric_column].resample(period).agg(['mean', 'median', 'std', 'count'])
        trend['rolling_avg_7'] = df_trend[metric_column].rolling(window=7).mean()

        return trend
