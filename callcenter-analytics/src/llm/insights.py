"""
Insight Generator Module
Generate AI-powered insights from KPI data
"""

import json
from typing import Dict, List, Optional
from .client import LLMClient
from .prompts import PromptTemplates


class InsightGenerator:
    """Generate insights using LLM based on KPI analysis"""

    def __init__(self, config: dict):
        self.config = config
        self.llm_client = LLMClient(config)
        self.prompts = PromptTemplates()
        self.system_prompt = self.prompts.get_system_prompt()

    def generate_kpi_summary(self, kpi_data: Dict) -> str:
        """
        Generate summary of KPI data

        Args:
            kpi_data: Dictionary with KPI metrics

        Returns:
            Summary text
        """
        print("\n🤖 Generating KPI summary...")

        prompt = self.prompts.summarize_kpi_data(kpi_data)
        summary = self.llm_client.generate(prompt, self.system_prompt)

        print("✓ Summary generated")
        return summary

    def identify_patterns(self, kpi_data: Dict, correlation_data: List) -> str:
        """
        Identify patterns and relationships in data

        Args:
            kpi_data: Dictionary with KPI metrics
            correlation_data: List of correlations

        Returns:
            Pattern analysis text
        """
        print("\n🤖 Identifying patterns...")

        prompt = self.prompts.identify_patterns(kpi_data, correlation_data)
        patterns = self.llm_client.generate(prompt, self.system_prompt)

        print("✓ Patterns identified")
        return patterns

    def generate_recommendations(self, kpi_data: Dict, issues: List[str]) -> str:
        """
        Generate actionable recommendations

        Args:
            kpi_data: Dictionary with KPI metrics
            issues: List of identified issues

        Returns:
            Recommendations text
        """
        print("\n🤖 Generating recommendations...")

        prompt = self.prompts.generate_recommendations(kpi_data, issues)
        recommendations = self.llm_client.generate(prompt, self.system_prompt)

        print("✓ Recommendations generated")
        return recommendations

    def perform_root_cause_analysis(self, metric: str, current: float,
                                   target: float, related_data: Dict) -> str:
        """
        Perform root cause analysis for KPI gap

        Args:
            metric: KPI metric name
            current: Current value
            target: Target value
            related_data: Related metrics data

        Returns:
            Root cause analysis text
        """
        print(f"\n🤖 Analyzing root cause for {metric}...")

        prompt = self.prompts.root_cause_analysis(metric, current, target, related_data)
        analysis = self.llm_client.generate(prompt, self.system_prompt)

        print("✓ Root cause analysis completed")
        return analysis

    def compare_periods(self, period1_data: Dict, period2_data: Dict,
                       period1_name: str = "Previous", period2_name: str = "Current") -> str:
        """
        Compare performance between two periods

        Args:
            period1_data: First period KPI data
            period2_data: Second period KPI data
            period1_name: Name for first period
            period2_name: Name for second period

        Returns:
            Comparison analysis text
        """
        print(f"\n🤖 Comparing {period1_name} vs {period2_name}...")

        prompt = self.prompts.compare_periods(period1_data, period2_data,
                                             period1_name, period2_name)
        comparison = self.llm_client.generate(prompt, self.system_prompt)

        print("✓ Period comparison completed")
        return comparison

    def generate_executive_summary(self, analysis_results: Dict) -> str:
        """
        Generate executive summary from full analysis

        Args:
            analysis_results: Complete analysis results

        Returns:
            Executive summary text
        """
        print("\n🤖 Generating executive summary...")

        prompt = self.prompts.executive_summary(analysis_results)
        summary = self.llm_client.generate(prompt, self.system_prompt)

        print("✓ Executive summary generated")
        return summary

    def explain_anomalies(self, anomalies: List[Dict]) -> str:
        """
        Explain detected anomalies

        Args:
            anomalies: List of anomaly data

        Returns:
            Anomaly explanation text
        """
        print("\n🤖 Explaining anomalies...")

        prompt = self.prompts.anomaly_explanation(anomalies)
        explanation = self.llm_client.generate(prompt, self.system_prompt)

        print("✓ Anomaly explanation generated")
        return explanation

    def generate_comprehensive_insights(self, kpi_data: Dict,
                                       correlation_data: Optional[List] = None,
                                       anomalies: Optional[List] = None) -> Dict[str, str]:
        """
        Generate comprehensive insights combining multiple analyses

        Args:
            kpi_data: Dictionary with KPI metrics
            correlation_data: Optional correlation analysis
            anomalies: Optional detected anomalies

        Returns:
            Dictionary with different insight sections
        """
        print("\n🤖 Generating comprehensive insights...")

        insights = {}

        # KPI Summary
        insights['summary'] = self.generate_kpi_summary(kpi_data)

        # Pattern Analysis
        if correlation_data:
            insights['patterns'] = self.identify_patterns(kpi_data, correlation_data)

        # Identify issues from KPI data
        issues = self._extract_issues_from_kpis(kpi_data)
        if issues:
            insights['recommendations'] = self.generate_recommendations(kpi_data, issues)

        # Anomaly Analysis
        if anomalies:
            insights['anomalies'] = self.explain_anomalies(anomalies)

        # Executive Summary
        insights['executive_summary'] = self.generate_executive_summary({
            'kpi_data': kpi_data,
            'summary': insights.get('summary', ''),
            'patterns': insights.get('patterns', ''),
            'recommendations': insights.get('recommendations', '')
        })

        print("\n✓ Comprehensive insights generated")
        return insights

    def _extract_issues_from_kpis(self, kpi_data: Dict) -> List[str]:
        """
        Extract potential issues from KPI data by comparing to thresholds

        Args:
            kpi_data: Dictionary with KPI metrics

        Returns:
            List of identified issues
        """
        issues = []
        thresholds = self.config.get('kpi_thresholds', {})

        for category, metrics in kpi_data.items():
            if category in thresholds:
                for metric, value in metrics.items():
                    # Map metric names to threshold keys
                    threshold_key = metric.replace('_avg', '').replace('_rate', '')

                    if threshold_key in thresholds[category]:
                        target = thresholds[category][threshold_key]

                        # Assume higher is better for most metrics
                        if value < target:
                            gap_pct = ((target - value) / target * 100) if target > 0 else 0
                            issues.append(
                                f"{metric} is below target: {value:.2f} vs {target:.2f} ({gap_pct:.1f}% gap)"
                            )

        return issues

    def custom_query(self, question: str, context_data: Dict) -> str:
        """
        Answer custom analysis questions

        Args:
            question: User's question
            context_data: Relevant context data

        Returns:
            Answer text
        """
        print(f"\n🤖 Answering custom query...")

        prompt = self.prompts.custom_analysis(question, context_data)
        answer = self.llm_client.generate(prompt, self.system_prompt)

        print("✓ Query answered")
        return answer
