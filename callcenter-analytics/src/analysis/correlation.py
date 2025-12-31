"""
Correlation Analyzer Module
Analyze relationships between KPI metrics
"""

import pandas as pd
import numpy as np
from scipy import stats
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from typing import Dict, List, Tuple, Optional


class CorrelationAnalyzer:
    """Analyze correlations and relationships between KPIs"""

    def __init__(self, config: dict):
        self.config = config
        self.correlation_threshold = config.get('analysis', {}).get('correlation_threshold', 0.3)

    def calculate_correlation_matrix(self, df: pd.DataFrame, method: str = 'pearson') -> pd.DataFrame:
        """
        Calculate correlation matrix

        Args:
            df: Input DataFrame
            method: 'pearson', 'spearman', or 'kendall'

        Returns:
            Correlation matrix DataFrame
        """
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        correlation_matrix = df[numeric_cols].corr(method=method)

        print(f"\n📊 Correlation Matrix ({method}):")
        print(f"  Size: {correlation_matrix.shape}")

        return correlation_matrix

    def find_strong_correlations(self, corr_matrix: pd.DataFrame,
                                 threshold: Optional[float] = None) -> List[Tuple[str, str, float]]:
        """
        Find pairs of variables with strong correlations

        Args:
            corr_matrix: Correlation matrix
            threshold: Minimum absolute correlation (uses config default if None)

        Returns:
            List of (var1, var2, correlation) tuples
        """
        if threshold is None:
            threshold = self.correlation_threshold

        strong_correlations = []

        for i in range(len(corr_matrix.columns)):
            for j in range(i + 1, len(corr_matrix.columns)):
                corr_value = corr_matrix.iloc[i, j]
                if abs(corr_value) >= threshold:
                    strong_correlations.append((
                        corr_matrix.columns[i],
                        corr_matrix.columns[j],
                        corr_value
                    ))

        # Sort by absolute correlation value
        strong_correlations.sort(key=lambda x: abs(x[2]), reverse=True)

        print(f"\n🔍 Found {len(strong_correlations)} strong correlations (threshold: {threshold})")
        for var1, var2, corr in strong_correlations[:10]:  # Show top 10
            print(f"  {var1} <-> {var2}: {corr:.3f}")

        return strong_correlations

    def perform_regression_analysis(self, df: pd.DataFrame, target: str,
                                    features: List[str]) -> Dict[str, any]:
        """
        Perform simple linear regression analysis

        Args:
            df: Input DataFrame
            target: Target variable
            features: List of feature variables

        Returns:
            Dictionary with regression results
        """
        from sklearn.linear_model import LinearRegression
        from sklearn.metrics import r2_score, mean_squared_error

        results = {}

        for feature in features:
            if feature not in df.columns or target not in df.columns:
                continue

            # Remove NaN values
            data = df[[feature, target]].dropna()

            if len(data) < 10:
                continue

            X = data[[feature]].values
            y = data[target].values

            # Fit model
            model = LinearRegression()
            model.fit(X, y)

            # Predictions
            y_pred = model.predict(X)

            # Metrics
            results[feature] = {
                'coefficient': model.coef_[0],
                'intercept': model.intercept_,
                'r2_score': r2_score(y, y_pred),
                'rmse': np.sqrt(mean_squared_error(y, y_pred)),
                'correlation': np.corrcoef(data[feature], data[target])[0, 1]
            }

        print(f"\n📈 Regression Analysis for {target}:")
        for feature, metrics in results.items():
            print(f"  {feature}:")
            print(f"    R² Score: {metrics['r2_score']:.3f}")
            print(f"    Correlation: {metrics['correlation']:.3f}")

        return results

    def perform_pca(self, df: pd.DataFrame, n_components: int = 3) -> Dict[str, any]:
        """
        Perform Principal Component Analysis

        Args:
            df: Input DataFrame
            n_components: Number of principal components

        Returns:
            Dictionary with PCA results
        """
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        data = df[numeric_cols].dropna()

        # Standardize data
        scaler = StandardScaler()
        scaled_data = scaler.fit_transform(data)

        # Perform PCA
        pca = PCA(n_components=min(n_components, len(numeric_cols)))
        principal_components = pca.fit_transform(scaled_data)

        # Create DataFrame with principal components
        pc_columns = [f'PC{i+1}' for i in range(pca.n_components_)]
        pc_df = pd.DataFrame(data=principal_components, columns=pc_columns)

        results = {
            'principal_components': pc_df,
            'explained_variance_ratio': pca.explained_variance_ratio_,
            'cumulative_variance': np.cumsum(pca.explained_variance_ratio_),
            'components': pd.DataFrame(
                pca.components_,
                columns=numeric_cols,
                index=pc_columns
            )
        }

        print(f"\n🔬 PCA Analysis:")
        print(f"  Components: {pca.n_components_}")
        print(f"  Explained Variance: {pca.explained_variance_ratio_}")
        print(f"  Cumulative Variance: {results['cumulative_variance']}")

        return results

    def identify_kpi_drivers(self, df: pd.DataFrame, target_kpi: str,
                            min_correlation: float = 0.3) -> List[Tuple[str, float]]:
        """
        Identify which factors drive a specific KPI

        Args:
            df: Input DataFrame
            target_kpi: Target KPI column name
            min_correlation: Minimum correlation to consider

        Returns:
            List of (driver, correlation) tuples sorted by impact
        """
        if target_kpi not in df.columns:
            raise ValueError(f"Target KPI '{target_kpi}' not found in DataFrame")

        numeric_cols = df.select_dtypes(include=[np.number]).columns
        correlations = []

        for col in numeric_cols:
            if col != target_kpi:
                corr = df[target_kpi].corr(df[col])
                if abs(corr) >= min_correlation:
                    correlations.append((col, corr))

        # Sort by absolute correlation
        correlations.sort(key=lambda x: abs(x[1]), reverse=True)

        print(f"\n🎯 Key Drivers for '{target_kpi}':")
        for driver, corr in correlations:
            direction = "positive" if corr > 0 else "negative"
            print(f"  {driver}: {corr:.3f} ({direction})")

        return correlations

    def analyze_relationships(self, df: pd.DataFrame) -> Dict[str, any]:
        """
        Comprehensive relationship analysis

        Args:
            df: Input DataFrame

        Returns:
            Dictionary with all relationship analyses
        """
        print("\n🔍 Analyzing relationships between variables...")

        results = {
            'correlation_matrix': self.calculate_correlation_matrix(df),
            'strong_correlations': None,
        }

        results['strong_correlations'] = self.find_strong_correlations(
            results['correlation_matrix']
        )

        # PCA if enough variables
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) >= 3:
            results['pca'] = self.perform_pca(df)

        print("\n✓ Relationship analysis completed")
        return results
