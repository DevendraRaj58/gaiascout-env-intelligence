from typing import Dict, List


class MissingVariableDetector:
    """
    Identifies environmental variables required for
    meaningful multi-metric ecological reasoning.
    """

    REQUIRED_VARIABLES = {
        "soil_health": [
            "organic_carbon_pct",
            "ph",
            "moisture_pct",
        ],
        "biodiversity": [
            "species_richness",
            "habitat_diversity",
        ],
        "climate": [
            "annual_rainfall_mm",
            "mean_temp_celsius",
        ],
        "human_impact": [
            "deforestation_rate_pct",
            "land_fragmentation",
        ],
    }

    def detect(
        self,
        provided_metrics: Dict[str, float],
        requested_domains: List[str] = None
    ) -> Dict:

        if requested_domains is None:
            requested_domains = list(
                self.REQUIRED_VARIABLES.keys()
            )

        missing_by_domain = {}

        for domain in requested_domains:

            required = self.REQUIRED_VARIABLES.get(
                domain,
                []
            )

            missing = [
                metric
                for metric in required
                if metric not in provided_metrics
                or provided_metrics[metric] is None
            ]

            if missing:
                missing_by_domain[domain] = missing

        total_missing = sum(
            len(metrics)
            for metrics in missing_by_domain.values()
        )

        return {
            "has_missing_variables": total_missing > 0,
            "total_missing": total_missing,
            "missing_by_domain": missing_by_domain
        }