"""
__init__.py for models package
"""
from .schemas import (
    EcoQuery, GaiaScoutResponse, EcoRecommendation,
    EcoStressScore, RetrievedKnowledge, SoilMetrics,
    BiodiversityMetrics, ClimateMetrics, HumanImpactMetrics,
    Severity, TimeHorizon, ConfidenceLevel, LandUseType, BiomeType,
    ScientificReference, MetricImpact, MetricAssessment,
    MissingVariableRequest, GeoContext, RainfallCategory
)

__all__ = [
    "EcoQuery", "GaiaScoutResponse", "EcoRecommendation",
    "EcoStressScore", "RetrievedKnowledge", "SoilMetrics",
    "BiodiversityMetrics", "ClimateMetrics", "HumanImpactMetrics",
    "Severity", "TimeHorizon", "ConfidenceLevel", "LandUseType", "BiomeType",
    "ScientificReference", "MetricImpact", "MetricAssessment",
    "MissingVariableRequest", "GeoContext", "RainfallCategory"
]
