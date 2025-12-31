"""
Basic Test Script - Without scipy/sklearn dependencies
Tests core functionality with sample data
"""

import sys
import os
import io

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

print("=" * 80)
print("CallCenter Analytics - Basic Test")
print("=" * 80)

# Test 1: Load Configuration
print("\n[1/5] Testing Configuration...")
try:
    from utils.config import ConfigManager
    config = ConfigManager('config.yaml')
    print(f"[OK] Configuration loaded: {len(config.to_dict())} sections")
except Exception as e:
    print(f"[FAIL] Configuration failed: {e}")
    sys.exit(1)

# Test 2: Load Data
print("\n[2/5] Testing Data Loading...")
try:
    from data.loader import DataLoader
    loader = DataLoader(config.to_dict())
    df = loader.load_csv('data/sample/sample_kpi_data.csv')
    df = loader.parse_dates(df, date_columns=['date'])  # Only parse 'date' column
    print(f"[OK] Data loaded: {len(df)} rows, {len(df.columns)} columns")
    print(f"  Columns: {', '.join(df.columns.tolist()[:5])}...")
except Exception as e:
    print(f"[FAIL] Data loading failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 3: Clean Data
print("\n[3/5] Testing Data Cleaning...")
try:
    from data.cleaner import DataCleaner
    cleaner = DataCleaner(config.to_dict())
    df_clean = cleaner.clean_data(df, remove_outliers=False)
    print(f"[OK] Data cleaned: {len(df_clean)} rows remain")
except Exception as e:
    print(f"[FAIL] Data cleaning failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 4: Validate Data
print("\n[4/5] Testing Data Validation...")
try:
    from data.validator import DataValidator
    validator = DataValidator(config.to_dict())
    results = validator.validate_all(df_clean)
    print(f"[OK] Data validated")
    print(f"  Total rows: {results['quality_report']['total_rows']}")
    print(f"  Numeric columns: {len(results['quality_report']['numeric_columns'])}")
except Exception as e:
    print(f"[FAIL] Data validation failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 5: Calculate KPIs
print("\n[5/5] Testing KPI Calculation...")
try:
    # Import directly to avoid scipy dependency from correlation module
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src', 'analysis'))
    from kpi import KPIAnalyzer
    kpi_analyzer = KPIAnalyzer(config.to_dict())
    kpi_results = kpi_analyzer.calculate_all_kpis(df_clean)

    print(f"[OK] KPIs calculated")
    print(f"\n  Performance KPIs:")
    for key, value in list(kpi_results['performance'].items())[:3]:
        print(f"    {key}: {value:.2f}")

    print(f"\n  Quality KPIs:")
    for key, value in list(kpi_results['quality'].items())[:3]:
        print(f"    {key}: {value:.2f}")

except Exception as e:
    print(f"[FAIL] KPI calculation failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "=" * 80)
print("[SUCCESS] ALL TESTS PASSED!")
print("=" * 80)
print("\nNote: Advanced features (correlation analysis, statistics) require scipy/sklearn")
print("Install with: pip install scipy scikit-learn")
