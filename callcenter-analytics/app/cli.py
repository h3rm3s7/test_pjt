"""
CLI Application
Command-line interface for KPI analysis
"""

import argparse
import os
import sys

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.data import DataLoader, DataCleaner, DataValidator
from src.analysis import KPIAnalyzer, CorrelationAnalyzer, StatisticalAnalyzer
from src.llm import InsightGenerator
from src.report import ReportGenerator, ChartGenerator
from src.utils import ConfigManager, setup_logger


def main():
    """Main CLI application"""
    parser = argparse.ArgumentParser(
        description='CallCenter Analytics - KPI Analysis Tool'
    )
    parser.add_argument(
        '--input', '-i',
        required=True,
        help='Path to input CSV file or directory'
    )
    parser.add_argument(
        '--config', '-c',
        default='config.yaml',
        help='Path to configuration file'
    )
    parser.add_argument(
        '--output', '-o',
        help='Output directory for reports (overrides config)'
    )
    parser.add_argument(
        '--format', '-f',
        choices=['docx', 'txt', 'html'],
        help='Report format (overrides config)'
    )
    parser.add_argument(
        '--no-llm',
        action='store_true',
        help='Skip LLM-based insights generation'
    )
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Verbose output'
    )

    args = parser.parse_args()

    # Load configuration
    config_manager = ConfigManager(args.config)
    config = config_manager.to_dict()

    # Setup logger
    log_level = 'DEBUG' if args.verbose else config.get('logging', {}).get('level', 'INFO')
    logger = setup_logger(level=log_level)

    logger.info("=" * 80)
    logger.info("CallCenter Analytics - Starting Analysis")
    logger.info("=" * 80)

    try:
        # Step 1: Load Data
        logger.info("\n[1/7] Loading data...")
        loader = DataLoader(config)

        if os.path.isfile(args.input):
            df = loader.load_csv(args.input)
        else:
            df = loader.load_from_directory(args.input)

        df = loader.parse_dates(df)
        logger.info(f"✓ Loaded {len(df)} rows, {len(df.columns)} columns")

        # Step 2: Validate Data
        logger.info("\n[2/7] Validating data...")
        validator = DataValidator(config)
        validation_results = validator.validate_all(df)

        if not validation_results['sufficient_data'][0]:
            logger.error("Insufficient data for analysis")
            return 1

        # Step 3: Clean Data
        logger.info("\n[3/7] Cleaning data...")
        cleaner = DataCleaner(config)
        df_clean = cleaner.clean_data(df, remove_outliers=False)

        # Step 4: Calculate KPIs
        logger.info("\n[4/7] Calculating KPIs...")
        kpi_analyzer = KPIAnalyzer(config)
        kpi_results = kpi_analyzer.calculate_all_kpis(df_clean)

        logger.info(f"✓ Performance KPIs: {len(kpi_results['performance'])}")
        logger.info(f"✓ Quality KPIs: {len(kpi_results['quality'])}")

        # Step 5: Analyze Correlations
        logger.info("\n[5/7] Analyzing correlations...")
        corr_analyzer = CorrelationAnalyzer(config)
        corr_results = corr_analyzer.analyze_relationships(df_clean)

        # Step 6: Generate Insights
        insights = {}
        if not args.no_llm:
            logger.info("\n[6/7] Generating AI insights...")
            try:
                insight_gen = InsightGenerator(config)
                insights = insight_gen.generate_comprehensive_insights(
                    kpi_data=kpi_results,
                    correlation_data=corr_results.get('strong_correlations', [])
                )
                logger.info(f"✓ Generated {len(insights)} insight sections")
            except Exception as e:
                logger.warning(f"⚠ Could not generate LLM insights: {str(e)}")
                logger.warning("Continuing without AI insights...")
        else:
            logger.info("\n[6/7] Skipping AI insights (--no-llm flag)")

        # Step 7: Generate Report
        logger.info("\n[7/7] Generating report...")

        # Create charts
        chart_gen = ChartGenerator(config)
        output_dir = args.output or config.get('report', {}).get('output_path', 'outputs')
        charts_dir = os.path.join(output_dir, 'charts')
        charts = chart_gen.generate_all_charts(
            kpi_results,
            corr_results.get('correlation_matrix'),
            charts_dir
        )

        # Generate report
        report_gen = ReportGenerator(config)
        if args.output:
            report_gen.output_path = args.output

        analysis_data = {
            'kpi_data': kpi_results,
            'correlation_data': corr_results,
            'statistics': validation_results['quality_report']
        }

        report_path = report_gen.create_comprehensive_report(
            analysis_data,
            insights,
            charts
        )

        logger.info("\n" + "=" * 80)
        logger.info("✓ ANALYSIS COMPLETE")
        logger.info("=" * 80)
        logger.info(f"Report saved to: {report_path}")
        logger.info(f"Charts saved to: {charts_dir}")
        logger.info("=" * 80)

        return 0

    except Exception as e:
        logger.error(f"\n✗ Error during analysis: {str(e)}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
