"""
Streamlit Web Application
Interactive dashboard for KPI analysis
"""

import streamlit as st
import pandas as pd
import os
import sys

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.data import DataLoader, DataCleaner, DataValidator
from src.analysis import KPIAnalyzer, CorrelationAnalyzer
from src.llm import InsightGenerator
from src.report import ChartGenerator
from src.utils import ConfigManager


def main():
    st.set_page_config(
        page_title="CallCenter Analytics",
        page_icon="📞",
        layout="wide"
    )

    st.title("📞 CallCenter Analytics Dashboard")
    st.markdown("---")

    # Load configuration
    config = ConfigManager().to_dict()

    # Sidebar
    st.sidebar.header("Configuration")

    # File upload
    uploaded_file = st.sidebar.file_uploader(
        "Upload KPI Data (CSV)",
        type=['csv']
    )

    # LLM settings
    use_llm = st.sidebar.checkbox("Use AI Insights", value=True)

    if uploaded_file is not None:
        # Load data
        with st.spinner("Loading data..."):
            loader = DataLoader(config)
            df = pd.read_csv(uploaded_file)

            st.success(f"✓ Loaded {len(df)} rows, {len(df.columns)} columns")

        # Display data preview
        st.subheader("📊 Data Preview")
        st.dataframe(df.head(10))

        # Data quality
        with st.expander("Data Quality Report"):
            validator = DataValidator(config)
            quality_report = validator.check_data_quality(df)

            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Rows", quality_report['total_rows'])
            with col2:
                st.metric("Total Columns", quality_report['total_columns'])
            with col3:
                st.metric("Duplicate Rows", quality_report['duplicate_rows'])

        # Clean data
        if st.button("Clean & Analyze Data"):
            with st.spinner("Cleaning data..."):
                cleaner = DataCleaner(config)
                df_clean = cleaner.clean_data(df, remove_outliers=False)

            st.success("✓ Data cleaned")

            # Calculate KPIs
            with st.spinner("Calculating KPIs..."):
                kpi_analyzer = KPIAnalyzer(config)
                kpi_results = kpi_analyzer.calculate_all_kpis(df_clean)

            # Display KPIs
            st.subheader("📈 Key Performance Indicators")

            # Performance KPIs
            st.markdown("### Performance Metrics")
            perf_cols = st.columns(4)
            for idx, (metric, value) in enumerate(list(kpi_results['performance'].items())[:4]):
                with perf_cols[idx % 4]:
                    st.metric(metric.upper(), f"{value:.2f}")

            # Quality KPIs
            st.markdown("### Quality Metrics")
            qual_cols = st.columns(4)
            for idx, (metric, value) in enumerate(list(kpi_results['quality'].items())[:4]):
                with qual_cols[idx % 4]:
                    st.metric(metric.upper(), f"{value:.2f}")

            # Correlation Analysis
            with st.spinner("Analyzing correlations..."):
                corr_analyzer = CorrelationAnalyzer(config)
                corr_matrix = corr_analyzer.calculate_correlation_matrix(df_clean)

            st.subheader("🔍 Correlation Analysis")
            st.dataframe(corr_matrix)

            # Generate charts
            st.subheader("📊 Visualizations")

            chart_gen = ChartGenerator(config)

            # KPI Dashboard
            import tempfile
            with tempfile.TemporaryDirectory() as tmpdir:
                dashboard_path = os.path.join(tmpdir, 'dashboard.png')
                chart_gen.create_kpi_dashboard(kpi_results, dashboard_path)
                st.image(dashboard_path, caption="KPI Dashboard")

                # Correlation Heatmap
                heatmap_path = os.path.join(tmpdir, 'heatmap.png')
                chart_gen.create_correlation_heatmap(corr_matrix, heatmap_path)
                st.image(heatmap_path, caption="Correlation Heatmap")

            # AI Insights
            if use_llm:
                st.subheader("🤖 AI-Generated Insights")

                with st.spinner("Generating insights..."):
                    try:
                        insight_gen = InsightGenerator(config)
                        insights = insight_gen.generate_comprehensive_insights(
                            kpi_data=kpi_results,
                            correlation_data=corr_analyzer.find_strong_correlations(corr_matrix)
                        )

                        # Display insights
                        if 'executive_summary' in insights:
                            st.markdown("### Executive Summary")
                            st.info(insights['executive_summary'])

                        if 'summary' in insights:
                            with st.expander("Detailed Analysis"):
                                st.write(insights['summary'])

                        if 'recommendations' in insights:
                            with st.expander("Recommendations"):
                                st.write(insights['recommendations'])

                    except Exception as e:
                        st.warning(f"⚠ Could not generate AI insights: {str(e)}")

    else:
        st.info("👈 Please upload a CSV file to begin analysis")

        # Sample data info
        st.subheader("Expected Data Format")
        st.markdown("""
        Your CSV should include columns for:

        **Performance Metrics:**
        - `handle_time`: Call handle time in seconds
        - `first_call_resolution`: Binary (1/0)
        - `calls_offered`: Total calls offered
        - `calls_answered`: Total calls answered

        **Quality Metrics:**
        - `qa_score`: Quality score (0-100)
        - `csat_score`: Customer satisfaction (1-5)
        - `nps_score`: Net Promoter Score (-100 to 100)
        - `compliance_pass`: Compliance status (1/0)
        """)


if __name__ == '__main__':
    main()
