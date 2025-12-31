"""
Chart Generator Module
Generate visualizations for KPI data
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from typing import Dict, List, Optional, Tuple
import os


class ChartGenerator:
    """Generate charts and visualizations for reports"""

    def __init__(self, config: dict):
        self.config = config
        self.style = 'seaborn-v0_8-darkgrid'
        sns.set_palette("husl")

    def create_kpi_dashboard(self, kpi_data: Dict, save_path: str) -> str:
        """
        Create KPI dashboard with multiple metrics

        Args:
            kpi_data: Dictionary with performance and quality KPIs
            save_path: Path to save the chart

        Returns:
            Path to saved chart
        """
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        fig.suptitle('Call Center KPI Dashboard', fontsize=16, fontweight='bold')

        # Extract data
        perf_kpis = kpi_data.get('performance', {})
        qual_kpis = kpi_data.get('quality', {})

        # Plot 1: Performance Metrics Bar Chart
        if perf_kpis:
            ax = axes[0, 0]
            metrics = list(perf_kpis.keys())[:5]  # Top 5
            values = [perf_kpis[m] for m in metrics]

            ax.barh(metrics, values, color='skyblue')
            ax.set_xlabel('Value')
            ax.set_title('Performance Metrics')
            ax.grid(axis='x', alpha=0.3)

        # Plot 2: Quality Metrics Bar Chart
        if qual_kpis:
            ax = axes[0, 1]
            metrics = list(qual_kpis.keys())[:5]  # Top 5
            values = [qual_kpis[m] for m in metrics]

            ax.barh(metrics, values, color='lightcoral')
            ax.set_xlabel('Value')
            ax.set_title('Quality Metrics')
            ax.grid(axis='x', alpha=0.3)

        # Plot 3: Combined Metrics Comparison
        ax = axes[1, 0]
        all_metrics = list(perf_kpis.keys())[:3] + list(qual_kpis.keys())[:3]
        all_values = [perf_kpis.get(m, qual_kpis.get(m, 0)) for m in all_metrics]

        ax.bar(range(len(all_metrics)), all_values, color=['skyblue']*3 + ['lightcoral']*3)
        ax.set_xticks(range(len(all_metrics)))
        ax.set_xticklabels([m[:15] for m in all_metrics], rotation=45, ha='right')
        ax.set_ylabel('Value')
        ax.set_title('Top Metrics Overview')
        ax.grid(axis='y', alpha=0.3)

        # Plot 4: Summary Text
        ax = axes[1, 1]
        ax.axis('off')
        summary_text = "KPI Summary\n\n"
        summary_text += f"Performance Metrics: {len(perf_kpis)}\n"
        summary_text += f"Quality Metrics: {len(qual_kpis)}\n\n"

        if perf_kpis:
            first_metric = list(perf_kpis.keys())[0]
            summary_text += f"{first_metric}: {perf_kpis[first_metric]:.2f}\n"
        if qual_kpis:
            first_metric = list(qual_kpis.keys())[0]
            summary_text += f"{first_metric}: {qual_kpis[first_metric]:.2f}\n"

        ax.text(0.1, 0.5, summary_text, fontsize=12, verticalalignment='center')

        plt.tight_layout()
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()

        return save_path

    def create_correlation_heatmap(self, corr_matrix: pd.DataFrame, save_path: str) -> str:
        """
        Create correlation heatmap

        Args:
            corr_matrix: Correlation matrix DataFrame
            save_path: Path to save the chart

        Returns:
            Path to saved chart
        """
        plt.figure(figsize=(12, 10))

        sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', center=0,
                   square=True, linewidths=1, cbar_kws={"shrink": 0.8},
                   fmt='.2f', vmin=-1, vmax=1)

        plt.title('KPI Correlation Matrix', fontsize=14, fontweight='bold', pad=20)
        plt.tight_layout()
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()

        return save_path

    def create_trend_chart(self, df: pd.DataFrame, date_column: str,
                          metric_columns: List[str], save_path: str) -> str:
        """
        Create trend line chart

        Args:
            df: DataFrame with time series data
            date_column: Name of date column
            metric_columns: List of metrics to plot
            save_path: Path to save the chart

        Returns:
            Path to saved chart
        """
        plt.figure(figsize=(14, 6))

        for metric in metric_columns[:5]:  # Max 5 metrics
            if metric in df.columns:
                plt.plot(df[date_column], df[metric], marker='o',
                        label=metric, linewidth=2, markersize=4)

        plt.xlabel('Date', fontsize=12)
        plt.ylabel('Value', fontsize=12)
        plt.title('KPI Trends Over Time', fontsize=14, fontweight='bold')
        plt.legend(loc='best', framealpha=0.9)
        plt.grid(True, alpha=0.3)
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()

        return save_path

    def create_distribution_plot(self, df: pd.DataFrame, column: str, save_path: str) -> str:
        """
        Create distribution plot (histogram + KDE)

        Args:
            df: Input DataFrame
            column: Column to plot
            save_path: Path to save the chart

        Returns:
            Path to saved chart
        """
        fig, axes = plt.subplots(1, 2, figsize=(14, 5))

        # Histogram
        axes[0].hist(df[column].dropna(), bins=30, color='skyblue',
                    edgecolor='black', alpha=0.7)
        axes[0].set_xlabel(column, fontsize=12)
        axes[0].set_ylabel('Frequency', fontsize=12)
        axes[0].set_title(f'Distribution of {column}', fontsize=12, fontweight='bold')
        axes[0].grid(axis='y', alpha=0.3)

        # Box plot
        axes[1].boxplot(df[column].dropna(), vert=True)
        axes[1].set_ylabel(column, fontsize=12)
        axes[1].set_title(f'Box Plot of {column}', fontsize=12, fontweight='bold')
        axes[1].grid(axis='y', alpha=0.3)

        plt.tight_layout()
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()

        return save_path

    def create_comparison_chart(self, data: Dict[str, float], title: str, save_path: str) -> str:
        """
        Create comparison bar chart

        Args:
            data: Dictionary of labels and values
            title: Chart title
            save_path: Path to save the chart

        Returns:
            Path to saved chart
        """
        plt.figure(figsize=(10, 6))

        labels = list(data.keys())
        values = list(data.values())
        colors = ['green' if v > 0 else 'red' for v in values]

        plt.bar(labels, values, color=colors, alpha=0.7, edgecolor='black')
        plt.axhline(y=0, color='black', linestyle='-', linewidth=0.5)
        plt.xlabel('Metrics', fontsize=12)
        plt.ylabel('Value', fontsize=12)
        plt.title(title, fontsize=14, fontweight='bold')
        plt.xticks(rotation=45, ha='right')
        plt.grid(axis='y', alpha=0.3)
        plt.tight_layout()
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()

        return save_path

    def create_scatter_plot(self, df: pd.DataFrame, x_column: str, y_column: str,
                           save_path: str, hue_column: Optional[str] = None) -> str:
        """
        Create scatter plot

        Args:
            df: Input DataFrame
            x_column: X-axis column
            y_column: Y-axis column
            save_path: Path to save the chart
            hue_column: Optional column for color coding

        Returns:
            Path to saved chart
        """
        plt.figure(figsize=(10, 6))

        if hue_column and hue_column in df.columns:
            sns.scatterplot(data=df, x=x_column, y=y_column, hue=hue_column,
                          s=100, alpha=0.6, edgecolor='black')
        else:
            plt.scatter(df[x_column], df[y_column], s=100, alpha=0.6,
                       edgecolor='black', c='skyblue')

        plt.xlabel(x_column, fontsize=12)
        plt.ylabel(y_column, fontsize=12)
        plt.title(f'{y_column} vs {x_column}', fontsize=14, fontweight='bold')
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()

        return save_path

    def generate_all_charts(self, kpi_data: Dict, corr_matrix: pd.DataFrame,
                          output_dir: str) -> Dict[str, str]:
        """
        Generate all standard charts

        Args:
            kpi_data: KPI data dictionary
            corr_matrix: Correlation matrix
            output_dir: Directory to save charts

        Returns:
            Dictionary mapping chart names to file paths
        """
        os.makedirs(output_dir, exist_ok=True)

        charts = {}

        print("\n📊 Generating charts...")

        # KPI Dashboard
        dashboard_path = os.path.join(output_dir, 'kpi_dashboard.png')
        charts['dashboard'] = self.create_kpi_dashboard(kpi_data, dashboard_path)
        print("  ✓ KPI Dashboard")

        # Correlation Heatmap
        if corr_matrix is not None and not corr_matrix.empty:
            heatmap_path = os.path.join(output_dir, 'correlation_heatmap.png')
            charts['heatmap'] = self.create_correlation_heatmap(corr_matrix, heatmap_path)
            print("  ✓ Correlation Heatmap")

        print(f"\n✓ Generated {len(charts)} charts in {output_dir}")

        return charts
