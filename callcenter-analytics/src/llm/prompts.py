"""
Prompt Templates Module
Contains prompt templates for various LLM tasks
"""

from typing import Dict, List


class PromptTemplates:
    """Collection of prompt templates for KPI analysis"""

    @staticmethod
    def get_system_prompt() -> str:
        """Get the main system prompt for call center analysis"""
        return """You are an expert call center consultant with deep knowledge in:
- Call center operations and best practices
- Key Performance Indicators (KPIs) analysis
- Quality management and customer satisfaction
- Workforce optimization
- Data-driven decision making

Your role is to analyze call center data and provide actionable insights,
recommendations, and strategic guidance. Be specific, data-driven, and practical
in your recommendations."""

    @staticmethod
    def summarize_kpi_data(kpi_data: Dict) -> str:
        """Generate prompt to summarize KPI data"""
        return f"""Analyze the following call center KPI data and provide a comprehensive summary:

{kpi_data}

Please provide:
1. Overall performance assessment
2. Key strengths identified in the data
3. Areas of concern or underperformance
4. Notable trends or patterns

Keep your analysis concise but insightful."""

    @staticmethod
    def identify_patterns(kpi_data: Dict, correlations: List) -> str:
        """Generate prompt to identify patterns"""
        return f"""Based on the following KPI data and correlations, identify key patterns and relationships:

KPI Data:
{kpi_data}

Correlations:
{correlations}

Please analyze:
1. Significant patterns in the data
2. Unexpected relationships between metrics
3. Potential cause-and-effect relationships
4. Patterns that require immediate attention

Provide specific examples from the data to support your analysis."""

    @staticmethod
    def generate_recommendations(kpi_data: Dict, issues: List[str]) -> str:
        """Generate prompt for recommendations"""
        issues_text = "\n".join([f"- {issue}" for issue in issues])

        return f"""Based on this call center KPI data and identified issues, provide actionable recommendations:

KPI Data:
{kpi_data}

Identified Issues:
{issues_text}

Please provide:
1. Top 3-5 priority recommendations
2. Specific action steps for each recommendation
3. Expected impact on KPIs
4. Implementation difficulty (low/medium/high)
5. Timeline for implementation

Focus on practical, achievable recommendations that will have measurable impact."""

    @staticmethod
    def root_cause_analysis(metric: str, current_value: float, target_value: float,
                           related_data: Dict) -> str:
        """Generate prompt for root cause analysis"""
        return f"""Perform a root cause analysis for the following KPI performance gap:

Metric: {metric}
Current Value: {current_value}
Target Value: {target_value}
Gap: {target_value - current_value}

Related Data:
{related_data}

Please analyze:
1. Potential root causes for the performance gap
2. Supporting evidence from the data
3. Which causes are most likely based on the data
4. Recommended areas for deeper investigation

Use a structured approach (5 Whys or Fishbone) where appropriate."""

    @staticmethod
    def predict_impact(proposed_change: str, current_kpis: Dict) -> str:
        """Generate prompt to predict impact of changes"""
        return f"""Predict the potential impact of the following proposed change on call center KPIs:

Proposed Change:
{proposed_change}

Current KPIs:
{current_kpis}

Please provide:
1. Which KPIs will likely be affected (positively or negatively)
2. Estimated magnitude of impact (%, specific numbers if possible)
3. Timeline for seeing results
4. Potential risks or unintended consequences
5. Recommended monitoring metrics

Base your predictions on industry best practices and typical outcomes."""

    @staticmethod
    def compare_periods(period1_data: Dict, period2_data: Dict,
                       period1_name: str = "Previous", period2_name: str = "Current") -> str:
        """Generate prompt to compare two time periods"""
        return f"""Compare call center performance between two periods:

{period1_name} Period:
{period1_data}

{period2_name} Period:
{period2_data}

Please analyze:
1. Key improvements and deteriorations
2. Percentage changes in critical metrics
3. Potential reasons for significant changes
4. Whether changes are statistically significant or just noise
5. Trends that should continue vs. trends that need intervention

Provide a balanced assessment with specific numbers."""

    @staticmethod
    def agent_coaching_insights(agent_data: Dict) -> str:
        """Generate prompt for agent coaching insights"""
        return f"""Based on this individual agent's performance data, provide coaching insights:

Agent Performance Data:
{agent_data}

Please provide:
1. Top strengths to reinforce
2. Areas needing improvement (prioritized)
3. Specific coaching recommendations
4. Training topics that would be beneficial
5. Realistic improvement goals for next review period

Be constructive and specific in your feedback."""

    @staticmethod
    def executive_summary(full_analysis: Dict) -> str:
        """Generate prompt for executive summary"""
        return f"""Create an executive summary of this call center analysis:

Full Analysis:
{full_analysis}

The summary should include:
1. Overall performance status (1-2 sentences)
2. Top 3 key findings
3. Top 3 priority actions
4. Expected outcomes from recommendations

Keep it concise (200-300 words) and focused on actionable insights for leadership."""

    @staticmethod
    def anomaly_explanation(anomalies: List[Dict]) -> str:
        """Generate prompt to explain detected anomalies"""
        return f"""Explain the following anomalies detected in call center data:

Anomalies:
{anomalies}

For each anomaly, provide:
1. Possible explanations (at least 2-3)
2. How concerning is this anomaly (low/medium/high)
3. Recommended investigation steps
4. Whether this could be a data quality issue

Consider both operational and technical factors."""

    @staticmethod
    def custom_analysis(question: str, context_data: Dict) -> str:
        """Generate prompt for custom analysis questions"""
        return f"""Answer the following question about call center performance:

Question: {question}

Context Data:
{context_data}

Provide a detailed, data-driven answer that:
1. Directly addresses the question
2. References specific data points
3. Provides actionable insights
4. Suggests follow-up analyses if relevant

Be thorough but concise."""

    @staticmethod
    def format_insights_for_report(insights: List[str]) -> str:
        """Generate prompt to format insights for a report"""
        insights_text = "\n".join([f"{i+1}. {insight}" for i, insight in enumerate(insights)])

        return f"""Format the following insights into a professional report section:

Raw Insights:
{insights_text}

Please:
1. Organize insights logically (group related items)
2. Add appropriate headings and subheadings
3. Ensure professional tone
4. Add transition sentences between sections
5. Highlight critical points

Output should be ready to include in a formal business report."""
