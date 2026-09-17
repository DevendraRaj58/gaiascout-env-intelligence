from typing import Dict, Any

from backend.knowledge.structured_db import (
    get_metric_severity,
    get_interventions_for_context,
)


class EcoMetricEngine:
    """
    Deterministic environmental reasoning engine.

    The LLM does NOT calculate environmental severity.
    This engine evaluates metrics using the structured
    scientific thresholds stored in SQLite.
    """

    def assess_metric(
        self,
        metric_name: str,
        value: float
    ) -> Dict[str, Any]:

        result = get_metric_severity(metric_name, value)

        if not result:
            return {
                "metric": metric_name,
                "value": value,
                "severity": "unknown",
                "reason": "No threshold available"
            }

        return {
            "metric": metric_name,
            "value": value,
            "severity": result.get("severity", "unknown"),
            "reason": result.get("description", ""),
            "unit": result.get("unit", "")
        }

    def calculate_stress_score(self, assessments):

        severity_weights = {
            "excellent": 0,
            "good": 10,
            "moderate": 40,
            "poor": 70,
            "critical": 100,
            "unknown": 0
        }

        if not assessments:
            return 0.0

        scores = [
            severity_weights.get(
                assessment["severity"],
                0
            )
            for assessment in assessments
        ]

        return round(sum(scores) / len(scores), 2)

    def identify_limiting_factors(
        self,
        assessments,
        top_n=3
    ):

        severity_order = {
            "critical": 5,
            "poor": 4,
            "moderate": 3,
            "good": 2,
            "excellent": 1,
            "unknown": 0
        }

        ranked = sorted(
            assessments,
            key=lambda x: severity_order.get(
                x["severity"],
                0
            ),
            reverse=True
        )

        return ranked[:top_n]

    def analyze(
        self,
        metrics: Dict[str, float],
        biome: str = None,
        land_use: str = None
    ) -> Dict[str, Any]:

        assessments = []

        for metric_name, value in metrics.items():

            if value is None:
                continue

            assessment = self.assess_metric(
                metric_name,
                value
            )

            assessments.append(assessment)

        stress_score = self.calculate_stress_score(
            assessments
        )

        limiting_factors = self.identify_limiting_factors(
            assessments
        )

        interventions = get_interventions_for_context(
            biome=biome,
            land_use=land_use,
            metrics=list(metrics.keys()),
            limit=5
        )

        return {
            "biome": biome,
            "land_use": land_use,
            "assessments": assessments,
            "environmental_stress_score": stress_score,
            "limiting_factors": limiting_factors,
            "candidate_interventions": interventions
        }