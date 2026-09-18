"""
schemas.py — GaiaScout Data Models

WHY THIS EXISTS:
  Every piece of data flowing through GaiaScout is typed here using Pydantic.
  This means:
    - The API validates incoming JSON automatically
    - The LLM must produce structured output (not freeform text)
    - The EcoMetricEngine has a guaranteed contract for inputs/outputs
    - The frontend knows exactly what shape each response has

  This is what separates a production system from a prototype.
"""

from __future__ import annotations
from enum import Enum
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, field_validator
import uuid
from datetime import datetime


# ─────────────────────────────────────────────────────────────
# ENUMS — Controlled vocabularies for categorical fields
# ─────────────────────────────────────────────────────────────

class Severity(str, Enum):
    """How critical is a metric's current value?"""
    CRITICAL = "critical"       # Immediate action required
    POOR     = "poor"           # Below threshold, declining
    MODERATE = "moderate"       # Acceptable but improvable
    GOOD     = "good"           # Healthy range
    EXCELLENT = "excellent"     # Optimal


class TimeHorizon(str, Enum):
    """When will the recommendation show measurable impact?"""
    SHORT  = "short"    # 0–12 months
    MEDIUM = "medium"   # 1–5 years
    LONG   = "long"     # 5–20 years


class ConfidenceLevel(str, Enum):
    """How confident is the system in this recommendation?"""
    HIGH   = "high"     # Multiple convergent studies, well-established science
    MEDIUM = "medium"   # Some supporting evidence, context-dependent
    LOW    = "low"      # Limited data, emerging research, or high variability


class LandUseType(str, Enum):
    """Standard LULC (Land Use / Land Cover) classification"""
    CROPLAND_MONOCULTURE = "cropland_monoculture"
    CROPLAND_MIXED       = "cropland_mixed"
    AGROFORESTRY         = "agroforestry"
    GRASSLAND            = "grassland"
    DEGRADED_LAND        = "degraded_land"
    FOREST_NATURAL       = "forest_natural"
    FOREST_PLANTATION    = "forest_plantation"
    WETLAND              = "wetland"
    URBAN                = "urban"
    BARREN               = "barren"


class BiomeType(str, Enum):
    """Major biome classifications"""
    TROPICAL_FOREST      = "tropical_forest"
    TEMPERATE_FOREST     = "temperate_forest"
    BOREAL_FOREST        = "boreal_forest"
    TROPICAL_GRASSLAND   = "tropical_grassland"
    TEMPERATE_GRASSLAND  = "temperate_grassland"
    MEDITERRANEAN        = "mediterranean"
    SEMI_ARID            = "semi_arid"
    ARID_DESERT          = "arid_desert"
    WETLAND              = "wetland"
    COASTAL_MARINE       = "coastal_marine"
    UNKNOWN              = "unknown"


class RainfallCategory(str, Enum):
    """Annual rainfall classification"""
    VERY_LOW  = "very_low"   # < 250 mm/year
    LOW       = "low"        # 250–500 mm/year
    MODERATE  = "moderate"   # 500–1000 mm/year
    HIGH      = "high"       # 1000–2000 mm/year
    VERY_HIGH = "very_high"  # > 2000 mm/year


# ─────────────────────────────────────────────────────────────
# INPUT MODELS — What the user/API sends to GaiaScout
# ─────────────────────────────────────────────────────────────

class SoilMetrics(BaseModel):
    """
    Soil health indicators.
    Sources for threshold values:
      - FAO (2020): "State of Knowledge of Soil Biodiversity"
      - USDA NRCS Soil Health Key Indicators
    """
    ph:                  Optional[float] = Field(None, ge=0, le=14,    description="Soil pH (0–14 scale)")
    organic_carbon_pct:  Optional[float] = Field(None, ge=0, le=20,   description="Soil organic carbon percentage")
    moisture_pct:        Optional[float] = Field(None, ge=0, le=100,  description="Volumetric soil moisture (%)")
    nitrogen_pct:        Optional[float] = Field(None, ge=0, le=5,    description="Total nitrogen (%)")
    bulk_density:        Optional[float] = Field(None, ge=0, le=2.5,  description="Bulk density (g/cm³)")
    erosion_risk:        Optional[str]   = Field(None,                 description="Erosion risk: none/low/medium/high/very_high")

    @validator("ph")
    @classmethod
    def ph_range(cls, v):
        if v is not None and not (0 <= v <= 14):
            raise ValueError("pH must be between 0 and 14")
        return v


class BiodiversityMetrics(BaseModel):
    """
    Biodiversity health indicators.
    Sources:
      - IUCN Red List Index methodology
      - CBD (Convention on Biological Diversity) Aichi Targets
    """
    species_richness:      Optional[int]   = Field(None, ge=0,    description="Number of distinct species observed")
    habitat_diversity:     Optional[float] = Field(None, ge=0, le=10, description="Shannon diversity index (H')")
    native_species_pct:    Optional[float] = Field(None, ge=0, le=100, description="% of native vs invasive species")
    pollinator_abundance:  Optional[str]   = Field(None,           description="Qualitative: none/low/moderate/high")
    endemic_species_count: Optional[int]   = Field(None, ge=0,    description="Number of endemic species present")


class ClimateMetrics(BaseModel):
    """
    Climate and weather metrics.
    Sources:
      - IPCC AR6 Regional Climate Chapters
      - WorldClim v2.1 Climate Data
    """
    annual_rainfall_mm:    Optional[float] = Field(None, ge=0,    description="Annual rainfall in mm")
    rainfall_category:     Optional[RainfallCategory] = Field(None, description="Qualitative rainfall class")
    mean_temp_celsius:     Optional[float] = Field(None, ge=-60, le=60, description="Mean annual temperature (°C)")
    drought_frequency:     Optional[str]   = Field(None,           description="Drought frequency: rare/occasional/frequent/persistent")
    extreme_events:        Optional[List[str]] = Field(None,       description="List of extreme event types experienced")


class HumanImpactMetrics(BaseModel):
    """
    Anthropogenic pressure indicators.
    Sources:
      - Global Forest Watch
      - WHO Air Quality Database
    """
    deforestation_rate_pct: Optional[float] = Field(None, ge=0, le=100, description="Annual deforestation rate (%)")
    pollution_level:         Optional[str]  = Field(None, description="Air/water pollution: none/low/moderate/high/critical")
    pesticide_use:           Optional[str]  = Field(None, description="Pesticide use intensity: none/low/moderate/high")
    land_fragmentation:      Optional[str]  = Field(None, description="Habitat fragmentation: intact/slightly/moderately/highly/severely")
    irrigation_type:         Optional[str]  = Field(None, description="Irrigation type: none/surface/drip/sprinkler/flood")


class GeoContext(BaseModel):
    """Optional geo-coordinates for biome inference (bonus feature)"""
    latitude:  Optional[float] = Field(None, ge=-90, le=90)
    longitude: Optional[float] = Field(None, ge=-180, le=180)
    country:   Optional[str]   = None
    region:    Optional[str]   = None


class EcoQuery(BaseModel):
    """
    The main input model — everything a user can provide to GaiaScout.

    WHY THIS STRUCTURE:
      Separating metrics by domain (soil/biodiversity/climate/human impact)
      mirrors how environmental scientists actually record and think about data.
      It also allows the MissingVariableDetector to know WHICH domain needs more info.
    """
    # Conversational fields
    session_id:     str          = Field(default_factory=lambda: str(uuid.uuid4()))
    user_message:   str          = Field(..., min_length=1, description="The user's natural language input")

    # Structured metric inputs (all optional — user may not have all data)
    land_use_type:  Optional[LandUseType]          = None
    biome:          Optional[BiomeType]            = None
    crop_type:      Optional[str]                  = None
    soil:           Optional[SoilMetrics]          = SoilMetrics()
    biodiversity:   Optional[BiodiversityMetrics]  = BiodiversityMetrics()
    climate:        Optional[ClimateMetrics]       = ClimateMetrics()
    human_impact:   Optional[HumanImpactMetrics]   = HumanImpactMetrics()
    geo:            Optional[GeoContext]           = None

    # Conversation history (populated by the backend across turns)
    conversation_history: List[Dict[str, str]] = Field(default_factory=list)


# ─────────────────────────────────────────────────────────────
# OUTPUT MODELS — What GaiaScout returns to the user
# ─────────────────────────────────────────────────────────────

class ScientificReference(BaseModel):
    """A citable scientific source backing a recommendation"""
    title:        str
    authors:      Optional[str] = None
    year:         Optional[int] = None
    organization: Optional[str] = None   # e.g., "FAO", "IPCC", "Nature"
    doi_or_url:   Optional[str] = None
    key_finding:  str                    # The specific finding we're citing


class MetricImpact(BaseModel):
    """Quantified impact on a specific environmental metric"""
    metric_name:        str              # e.g., "Soil Organic Carbon"
    current_severity:   Optional[Severity] = None
    expected_change:    str              # e.g., "+15–25% over 3 years"
    improvement_after:  Optional[str]   = None   # e.g., "MODERATE after 3 years"


class EcoRecommendation(BaseModel):
    """
    A single structured recommendation from GaiaScout.

    WHY THIS SCHEMA MATTERS:
      The challenge explicitly says each recommendation must have:
        - What to do ✓ (action_title + action_description)
        - Why it works ✓ (mechanism + references)
        - Which metric improves ✓ (metric_impacts)
        - Time horizon ✓ (time_horizon)
      Plus our extras: confidence, limiting_factor (which variable drove this),
      and the retrieved_chunks that prove we used RAG (not just prompting).
    """
    rank:               int                          # Priority rank (1 = most urgent)
    action_title:       str                          # Short name: e.g., "Legume Cover Cropping"
    action_description: str                          # Full explanation of what to do
    mechanism:          str                          # The scientific WHY (biochemical/ecological)
    limiting_factor:    str                          # Which variable triggered this recommendation
    metric_impacts:     List[MetricImpact]           # Quantified impacts per metric
    time_horizon:       TimeHorizon
    confidence:         ConfidenceLevel
    references:         List[ScientificReference]    # Cited sources
    retrieved_chunks:   List[str] = Field(          # RAG transparency — show what was retrieved
        default_factory=list,
        description="Excerpts from knowledge base used to generate this recommendation"
    )
    implementation_steps: Optional[List[str]] = None  # Step-by-step action plan


class MetricAssessment(BaseModel):
    """Assessment of a single environmental metric"""
    metric_name: str
    value:       Optional[Any]   = None
    severity:    Severity
    explanation: str             # Why this severity was assigned


class MissingVariableRequest(BaseModel):
    """When the system needs more info — structured clarification request"""
    missing_domain:    str                  # e.g., "soil", "climate"
    missing_variables: List[str]            # e.g., ["soil_pH", "organic_carbon_pct"]
    question:          str                  # Natural language question to ask the user
    why_needed:        str                  # Scientific reason this data matters


class GaiaScoutResponse(BaseModel):
    """
    The complete response envelope from GaiaScout.

    TYPES OF RESPONSE:
      1. CLARIFICATION: System needs more data (MissingVariableRequest)
      2. ASSESSMENT:    Full analysis with recommendations
      3. CONVERSATIONAL: A follow-up explanation in an ongoing dialogue
    """
    response_type:       str                               # "clarification" | "assessment" | "conversational"
    session_id:          str
    timestamp:           str = Field(default_factory=lambda: datetime.utcnow().isoformat())

    # For ASSESSMENT responses
    metric_assessments:  Optional[List[MetricAssessment]]     = None
    limiting_factors:    Optional[List[str]]                  = None   # Top bottlenecks found by EcoMetricEngine
    recommendations:     Optional[List[EcoRecommendation]]    = None
    summary:             Optional[str]                        = None   # High-level summary paragraph

    # For CLARIFICATION responses
    clarification:       Optional[MissingVariableRequest]     = None

    # For CONVERSATIONAL responses
    message:             Optional[str]                        = None

    # Metadata (for transparency / debugging)
    variables_used:      List[str] = Field(default_factory=list)  # Which metrics were provided
    knowledge_retrieved: bool = False                              # Did RAG retrieve anything?
    retrieval_sources:   List[str] = Field(default_factory=list)  # Source doc names used


# ─────────────────────────────────────────────────────────────
# INTERNAL ENGINE MODELS
# ─────────────────────────────────────────────────────────────

class EcoStressScore(BaseModel):
    """
    Output of EcoMetricEngine's multi-variable analysis.
    This is an INTERNAL model — not exposed to the user directly.

    WHY A SEPARATE SCORE MODEL:
      The EcoMetricEngine computes this BEFORE the LLM is called.
      The LLM then uses this as structured context, not raw numbers.
      This prevents the LLM from "making up" stress levels.
    """
    overall_score:      float                     # 0 (healthy) to 1 (critical)
    domain_scores: Dict[str, float]               # Per-domain: soil/biodiv/climate/human
    limiting_factors:   List[str]                 # Top 3 Liebig-principle bottlenecks
    severity_map:  Dict[str, Severity]            # Per-metric severity
    intervention_candidates: List[str]            # Ranked list of intervention types


class RetrievedKnowledge(BaseModel):
    """Output of the hybrid retriever — what was found in the knowledge base"""
    chunks:    List[str]                          # The actual text chunks retrieved
    sources:   List[str]                          # Source document names
    scores:    List[float]                        # Relevance scores
    method:    str                                # "semantic" | "keyword" | "hybrid"
