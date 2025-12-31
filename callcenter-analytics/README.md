# CallCenter Analytics & AI Reporting System

A comprehensive Python application for analyzing call center KPI data and generating AI-powered insights and reports.

## Features

- 📊 **KPI Analysis**: Calculate performance and quality metrics
- 🔍 **Correlation Analysis**: Identify relationships between metrics
- 🤖 **AI Insights**: Generate insights using LLM (OpenAI, Anthropic, or local Ollama)
- 📈 **Visualizations**: Create charts and dashboards
- 📝 **Reports**: Generate comprehensive PDF/DOCX reports
- 🖥️ **Dual Interface**: CLI and Web UI (Streamlit)

## Installation

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Setup

1. Clone or download this project

2. Install dependencies:
```bash
cd callcenter-analytics
pip install -r requirements.txt
```

3. Configure API keys:
```bash
# Copy example env file
copy .env.example .env

# Edit .env and add your API key
# OPENAI_API_KEY=your_key_here
```

4. (Optional) Customize configuration:
   - Edit `config.yaml` to adjust KPI thresholds, analysis settings, etc.

## Usage

### CLI Mode

Basic usage:
```bash
python app/cli.py --input data/sample/sample_kpi_data.csv
```

With options:
```bash
python app/cli.py --input data/raw/kpi_data.csv --output reports --format docx --verbose
```

Options:
- `--input, -i`: Path to CSV file or directory (required)
- `--config, -c`: Path to config file (default: config.yaml)
- `--output, -o`: Output directory for reports
- `--format, -f`: Report format (docx, txt, html)
- `--no-llm`: Skip AI insights generation
- `--verbose, -v`: Verbose output

### Web UI (Streamlit)

Launch the dashboard:
```bash
streamlit run app/main.py
```

Then:
1. Upload your CSV file
2. Configure settings in sidebar
3. Click "Clean & Analyze Data"
4. View results and download reports

## Data Format

Your CSV should include these columns:

### Performance Metrics
- `handle_time`: Call handle time (seconds)
- `first_call_resolution`: FCR status (1/0)
- `calls_offered`: Total calls offered
- `calls_answered`: Calls answered
- `answer_time`: Time to answer (seconds)
- `logged_time`: Agent logged time
- `productive_time`: Agent productive time

### Quality Metrics
- `qa_score`: Quality score (0-100)
- `csat_score`: Customer satisfaction (1-5)
- `nps_score`: Net Promoter Score (-100 to 100)
- `compliance_pass`: Compliance status (1/0)
- `error_count`: Number of errors
- `total_interactions`: Total interactions

### Optional
- `date`: Date column for trend analysis
- `agent_id`: For agent-level analysis
- `team`: For team comparison

## Project Structure

```
callcenter-analytics/
├── data/                   # Data files
│   ├── raw/               # Original data
│   ├── processed/         # Cleaned data
│   └── sample/            # Sample datasets
├── src/                    # Source code
│   ├── data/              # Data processing
│   ├── analysis/          # KPI analysis
│   ├── llm/               # LLM integration
│   ├── report/            # Report generation
│   └── utils/             # Utilities
├── app/                    # Applications
│   ├── cli.py             # CLI interface
│   └── main.py            # Streamlit app
├── outputs/                # Generated reports
├── config.yaml            # Configuration
├── requirements.txt       # Dependencies
└── README.md              # This file
```

## Configuration

Edit `config.yaml` to customize:

- LLM provider and model
- KPI target thresholds
- Analysis parameters
- Report settings

## Examples

### Example 1: Basic Analysis
```bash
python app/cli.py -i data/sample/sample_kpi_data.csv
```

### Example 2: Without AI Insights
```bash
python app/cli.py -i data/raw/monthly_data.csv --no-llm
```

### Example 3: Custom Output
```bash
python app/cli.py -i data/raw/q1_data.csv -o reports/q1 -f docx -v
```

## Troubleshooting

### No API Key Error
- Make sure you've created `.env` file and added your API key
- Check that the environment variable name matches config.yaml

### Import Errors
- Ensure all dependencies are installed: `pip install -r requirements.txt`
- Try upgrading pip: `python -m pip install --upgrade pip`

### Data Loading Issues
- Verify CSV format and encoding (UTF-8 recommended)
- Check column names match expected format
- Ensure data has sufficient rows (minimum 30)

## Development

### Adding New KPIs

1. Edit `src/analysis/kpi.py`
2. Add calculation in `calculate_performance_kpis()` or `calculate_quality_kpis()`
3. Update `config.yaml` with targets

### Custom LLM Prompts

1. Edit `src/llm/prompts.py`
2. Add new prompt template method
3. Use in `src/llm/insights.py`

## License

This project is for internal use.

## Support

For issues or questions:
1. Check the troubleshooting section
2. Review sample data format
3. Verify configuration settings

---

**Version**: 0.1.0
**Last Updated**: 2025-12-30
