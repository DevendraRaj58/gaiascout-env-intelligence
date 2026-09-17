"""
GaiaScout LangGraph Agent — Orchestrates the environmental intelligence flow.

This agent implements the core decision flow:
1. Understand user intent and extract metrics
2. Check for missing critical variables
3. If sufficient data: calculate stress, identify limiting factors
4. Retrieve relevant scientific evidence
5. Generate structured, evidence-backed recommendation
6. Handle multi-turn conversation with memory

WHY LANGGRAPH:
- Provides stateful, check-pointed conversation flow
- Enables conditional routing (clarify vs recommend)
- Makes the reasoning process transparent and debuggable
- Supports human-in-the-loop interventions if needed
"""

from typing import Dict, Any, List, Optional
from langgraph.graph import StateGraph, END
from langchain_core.runnables import RunnableConfig
from pydantic import BaseModel, Field
import json
import os
from datetime import datetime

# Import our existing components
from backend.models.schemas import (
    EcoQuery, GaiaScoutResponse, MissingVariableRequest,
    EcoRecommendation, MetricImpact, ScientificReference,
    ConfidenceLevel, TimeHorizon
)
from backend.engine.eco_metric_engine import EcoMetricEngine
from backend.engine.missing_variable import MissingVariableDetector
from backend.knowledge.vector_store import HybridRetriever


# ─────────────────────────────────────────────────────────────
# AGENT STATE — What flows between nodes
# ─────────────────────────────────────────────────────────────

class AgentState(BaseModel):
    """The state that persists across the LangGraph execution."""
    # Input
    query: EcoQuery
    
    # Processing flags
    has_sufficient_data: bool = False
    missing_vars: Dict[str, List[str]] = {}
    
    # EcoMetricEngine outputs
    assessments: List[Dict[str, Any]] = []
    stress_score: float = 0.0
    limiting_factors: List[Dict[str, Any]] = []
    intervention_candidates: List[Dict[str, Any]] = []
    
    # Retrieval outputs
    retrieved_chunks: List[str] = []
    retrieval_sources: List[str] = []
    knowledge_retrieved: bool = False
    
    # Final outputs
    recommendations: List[EcoRecommendation] = []
    clarification_request: Optional[MissingVariableRequest] = None
    summary: Optional[str] = None
    
    # Metadata
    session_id: str = ""
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    variables_used: List[str] = []
    response_type: str = "assessment"  # "assessment" | "clarification" | "conversational"
    message: Optional[str] = None


# ─────────────────────────────────────────────────────────────
# NODE IMPLEMENTATIONS
# ─────────────────────────────────────────────────────────────

def understand_node(state: AgentState) -> AgentState:
    """
    Extract and validate user input.
    Populates variables_used and prepares for missing variable check.
    """
    query = state.query
    
    # Flatten all provided metrics for easy checking
    provided_metrics = {}
    
    # Soil metrics
    if query.soil:
        soil_dict = query.soil.model_dump(exclude_unset=True)
        for k, v in soil_dict.items():
            if v is not None:
                provided_metrics[f"soil_{k}"] = v
    
    # Biodiversity metrics
    if query.biodiversity:
        bio_dict = query.biodiversity.model_dump(exclude_unset=True)
        for k, v in bio_dict.items():
            if v is not None:
                provided_metrics[f"biodiversity_{k}"] = v
    
    # Climate metrics
    if query.climate:
        climate_dict = query.climate.model_dump(exclude_unset=True)
        for k, v in climate_dict.items():
            if v is not None:
                provided_metrics[f"climate_{k}"] = v
    
    # Human impact metrics
    if query.human_impact:
        human_dict = query.human_impact.model_dump(exclude_unset=True)
        for k, v in human_dict.items():
            if v is not None:
                provided_metrics[f"human_impact_{k}"] = v
    
    # Update state
    state.variables_used = list(provided_metrics.keys())
    state.query = query  # Keep the original query
    
    return state


def missing_variable_check_node(state: AgentState) -> AgentState:
    """
    Determine if we have sufficient data for multi-metric reasoning.
    If not, prepare a clarification request.
    """
    detector = MissingVariableDetector()
    
    # Prepare metrics dict for detector (flat key-value pairs) with prefixes removed
    provided_metrics = {}
    for var in state.variables_used:
        # Extract value from query based on variable name
        # This is a simplified version - in production you'd want a more robust mapping
        if var.startswith("soil_") and state.query.soil:
            attr_name = var.replace("soil_", "")
            value = getattr(state.query.soil, attr_name, None)
            if value is not None:
                provided_metrics[var] = value
        elif var.startswith("biodiversity_") and state.query.biodiversity:
            attr_name = var.replace("biodiversity_", "")
            value = getattr(state.query.biodiversity, attr_name, None)
            if value is not None:
                provided_metrics[var] = value
        elif var.startswith("climate_") and state.query.climate:
            attr_name = var.replace("climate_", "")
            value = getattr(state.query.climate, attr_name, None)
            if value is not None:
                provided_metrics[var] = value
        elif var.startswith("human_impact_") and state.query.human_impact:
            attr_name = var.replace("human_impact_", "")
            value = getattr(state.query.human_impact, attr_name, None)
            if value is not None:
                provided_metrics[var] = value
    
    # Convert provided_metrics (with prefixes) to base metrics for the detector
    base_metrics = {}
    for key, value in provided_metrics.items():
        if key.startswith("soil_"):
            base_metrics[key.replace("soil_", "")] = value
        elif key.startswith("biodiversity_"):
            base_metrics[key.replace("biodiversity_", "")] = value
        elif key.startswith("climate_"):
            base_metrics[key.replace("climate_", "")] = value
        elif key.startswith("human_impact_"):
            base_metrics[key.replace("human_impact_", "")] = value
        else:
            base_metrics[key] = value
    
    # Debug prints
    print(f"DEBUG: provided_metrics (with prefixes): {provided_metrics}")
    print(f"DEBUG: base_metrics (for detector): {base_metrics}")
    
    # Run detection
    detection_result = detector.detect(base_metrics)
    
    print(f"DEBUG: detection_result: {detection_result}")
    
    state.has_sufficient_data = not detection_result["has_missing_variables"]
    state.missing_vars = detection_result["missing_by_domain"]
    
    # If we're missing critical variables, prepare clarification
    if detection_result["has_missing_variables"]:
        # Build a natural language question based on missing domains
        missing_domains = list(detection_result["missing_by_domain"].keys())
        missing_vars_flat = []
        for domain, vars_list in detection_result["missing_by_domain"].items():
            missing_vars_flat.extend(vars_list)
        
        # Create a contextual question
        question_parts = []
        if "soil_health" in missing_domains:
            question_parts.append("soil health indicators (like soil organic carbon %, pH, or moisture)")
        if "biodiversity" in missing_domains:
            question_parts.append("biodiversity metrics (such as species richness or habitat diversity)")
        if "climate_factors" in missing_domains:
            question_parts.append("climate information (rainfall, temperature patterns)")
        if "human_impact" in missing_domains:
            question_parts.append("human impact factors (deforestation rate, pollution levels)")
        
        question = f"To give you a scientifically-grounded recommendation, I need some additional information about: {', '.join(question_parts)}. "
        question += "Could you provide any of these metrics for your location?"
        
        state.clarification_request = MissingVariableRequest(
            missing_domain=", ".join(missing_domains),
            missing_variables=missing_vars_flat,
            question=question,
            why_needed="Multi-metric environmental reasoning requires data from multiple domains to avoid misleading single-variable recommendations."
        )
        state.response_type = "clarification"
    else:
        state.response_type = "assessment"  # Default to assessment if sufficient data
        state.message = None
    
    return state


def eco_engine_node(state: AgentState) -> AgentState:
    """
    Run the deterministic environmental reasoning engine.
    Only executes if we have sufficient data.
    """
    if not state.has_sufficient_data:
        return state
    
    engine = EcoMetricEngine()
    
    # Rebuild metrics dict for the engine
    metrics = {}
    if state.query.soil:
        soil_dict = state.query.soil.model_dump(exclude_unset=True)
        for k, v in soil_dict.items():
            if v is not None:
                metrics[k] = v
    if state.query.biodiversity:
        bio_dict = state.query.biodiversity.model_dump(exclude_unset=True)
        for k, v in bio_dict.items():
            if v is not None:
                metrics[k] = v
    if state.query.climate:
        climate_dict = state.query.climate.model_dump(exclude_unset=True)
        for k, v in climate_dict.items():
            if v is not None:
                metrics[k] = v
    if state.query.human_impact:
        human_dict = state.query.human_impact.model_dump(exclude_unset=True)
        for k, v in human_dict.items():
            if v is not None:
                metrics[k] = v
    
    # Run analysis
    biome = state.query.biome.value if state.query.biome else None
    land_use = state.query.land_use_type.value if state.query.land_use_type else None
    
    result = engine.analyze(metrics, biome=biome, land_use=land_use)
    
    state.assessments = result["assessments"]
    state.stress_score = result["environmental_stress_score"]
    state.limiting_factors = result["limiting_factors"]
    state.intervention_candidates = result["candidate_interventions"]
    
    return state


def retrieval_node(state: AgentState) -> AgentState:
    """
    Retrieve relevant scientific evidence from the knowledge base.
    Uses hybrid search (ChromaDB + BM25) for best results.
    """
    if not state.has_sufficient_data:
        return state
    
    # Build a search query based on the user's context and limiting factors
    query_parts = []
    
    # Add user's original message
    query_parts.append(state.query.user_message)
    
    # Add context from metrics
    if state.query.soil:
        if state.query.soil.organic_carbon_pct is not None:
            query_parts.append(f"soil organic carbon {state.query.soil.organic_carbon_pct}%")
    if state.query.climate:
        if state.query.climate.annual_rainfall_mm is not None:
            query_parts.append(f"rainfall {state.query.climate.annual_rainfall_mm}mm/year")
    
    # Add limiting factors focus
    for lf in state.limiting_factors:
        metric_name = lf.get("metric", "")
        severity = lf.get("severity", "")
        if metric_name and severity:
            query_parts.append(f"{metric_name} {severity}")
    
    search_query = " ".join(query_parts)
    
    try:
        retriever = HybridRetriever(top_k=5)
        results = retriever.search(search_query)
        
        state.retrieved_chunks = [r["text"] for r in results]
        state.retrieval_sources = [r["metadata"]["source"] for r in results]
        state.knowledge_retrieved = len(results) > 0
        
    except Exception as e:
        # Fallback if retrieval fails
        state.knowledge_retrieved = False
        state.retrieved_chunks = []
        state.retrieval_sources = []
        # In production, you'd want to log this error
    
    return state


def reasoning_node(state: AgentState) -> AgentState:
    """
    Generate evidence-backed recommendations using the LLM.
    This is where we would call Ollama/OpenAI/etc., but for MVP we'll
    use the structured intervention data from SQLite with enhancements.
    """
    if not state.has_sufficient_data:
        return state
    
    recommendations = []
    
    # For each intervention candidate, create a structured recommendation
    for i, intervention in enumerate(state.intervention_candidates[:3]):  # Top 3
        # Extract intervention details
        name = intervention.get("name", f"Intervention {i+1}")
        mechanism = intervention.get("mechanism", "")
        action_desc = intervention.get("action_description", "")
        time_horizon_str = intervention.get("time_horizon", "medium")
        confidence_str = intervention.get("confidence", "medium")
        
        # Parse time horizon
        try:
            time_horizon = TimeHorizon(time_horizon_str.lower())
        except:
            time_horizon = TimeHorizon.MEDIUM
        
        # Parse confidence
        try:
            confidence = ConfidenceLevel(confidence_str.lower())
        except:
            confidence = ConfidenceLevel.MEDIUM
        
        # Build metric impacts from intervention data
        metric_impacts = []
        impacts_json = intervention.get("metric_impacts", "[]")
        try:
            impacts_list = json.loads(impacts_json)
            for impact in impacts_list:
                metric_impacts.append(MetricImpact(
                    metric_name=impact.get("metric", ""),
                    expected_change=impact.get("change", ""),
                    improvement_after=None  # Could be enhanced later
                ))
        except:
            # Fallback if JSON parsing fails
            pass
        
        # Build references
        references = []
        refs_json = intervention.get("source_refs", "[]")
        try:
            refs_list = json.loads(refs_json)
            # In a full implementation, we'd look up the actual study details
            # For now, we'll create basic references
            for ref_key in refs_list:
                references.append(ScientificReference(
                    title=ref_key.replace("_", " ").title(),
                    organization="Various",
                    key_finding="Scientific evidence supports this intervention"
                ))
        except:
            # Fallback reference
            references.append(ScientificReference(
                title="Peer-reviewed environmental science",
                organization="Scientific Consensus",
                key_finding="Evidence-based intervention for ecosystem improvement"
            ))
        
        # Determine limiting factor (what this recommendation addresses)
        limiting_factor = state.limiting_factors[0]["metric"] if state.limiting_factors else "unknown"
        
        recommendation = EcoRecommendation(
            rank=i+1,
            action_title=name,
            action_description=action_desc,
            mechanism=mechanism,
            limiting_factor=limiting_factor,
            metric_impacts=metric_impacts,
            time_horizon=time_horizon,
            confidence=confidence,
            references=references,
            retrieved_chunks=state.retrieved_chunks[:2],  # Show top 2 retrieved chunks
            implementation_steps=json.loads(intervention.get("implementation_steps", "[]"))
        )
        
        recommendations.append(recommendation)
    
    state.recommendations = recommendations
    
    # Generate a summary paragraph
    if recommendations:
        top_rec = recommendations[0]
        state.summary = (
            f"Based on your environmental metrics showing {state.stress_score:.1f}% stress, "
            f"I recommend {top_rec.action_title.lower()}. {top_rec.action_description} "
            f"This addresses the {top_rec.limiting_factor} limitation and is expected to "
            f"{top_rec.metric_impacts[0].expected_change if top_rec.metric_impacts else 'improve key metrics'} "
            f"over {top_rec.time_horizon.value} term."
        )
    else:
        state.summary = "Unable to generate specific recommendations with current data. Please provide more environmental metrics."
    
    return state


def response_node(state: AgentState) -> AgentState:
    """
    Format the final response based on the processing path taken.
    """
    state.session_id = state.query.session_id
    
    if state.response_type == "clarification":
        # Return clarification request
        pass  # clarification_request is already set
    elif state.response_type == "assessment":
        # Return full assessment with recommendations
        pass  # recommendations and summary are already set
    else:
        # Fallback conversational response
        state.response_type = "conversational"
        state.message = "I'm here to help with your environmental questions. Could you share more details about your ecosystem?"
    
    return state


# ─────────────────────────────────────────────────────────────
# GRAPH CONSTRUCTION
# ─────────────────────────────────────────────────────────────

def create_gaiaScout_graph() -> StateGraph:
    """
    Construct the LangGraph state machine for GaiaScout.
    """
    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("understand", understand_node)
    workflow.add_node("missing_variable_check", missing_variable_check_node)
    workflow.add_node("eco_engine", eco_engine_node)
    workflow.add_node("retrieval", retrieval_node)
    workflow.add_node("reasoning", reasoning_node)
    workflow.add_node("response", response_node)
    
    # Define the flow
    workflow.set_entry_point("understand")
    
    # Always check for missing variables after understanding
    workflow.add_edge("understand", "missing_variable_check")
    
    # Conditional routing based on data sufficiency
    def should_continue(state: AgentState) -> str:
        if state.has_sufficient_data:
            return "eco_engine"
        else:
            return "response"  # Go straight to response for clarification
    
    workflow.add_conditional_edges(
        "missing_variable_check",
        should_continue,
        {
            "eco_engine": "eco_engine",
            "response": "response"
        }
    )
    
    # If we have sufficient data, continue through the pipeline
    workflow.add_edge("eco_engine", "retrieval")
    workflow.add_edge("retrieval", "reasoning")
    workflow.add_edge("reasoning", "response")
    
    # Response node always ends the flow
    workflow.add_edge("response", END)
    
    return workflow.compile()


# ─────────────────────────────────────────────────────────────
# PUBLIC INTERFACE
# ─────────────────────────────────────────────────────────────

class GaiaScoutAgent:
    """
    Public interface for the GaiaScout environmental intelligence agent.
    """
    
    def __init__(self):
        self.graph = create_gaiaScout_graph()
    
    def invoke(self, query: EcoQuery, config: Optional[RunnableConfig] = None) -> GaiaScoutResponse:
        """
        Process a user query and return a GaiaScoutResponse.
        """
        # Initialize state
        initial_state = AgentState(query=query)
        
        # Run the graph
        final_state = self.graph.invoke(initial_state, config=config or {})
        
        # LangGraph may return a dict-like object (AddableValuesDict) instead of AgentState
        # Convert to AgentState if needed
        if isinstance(final_state, dict):
            # Convert the query dict back to an EcoQuery if it's a dict
            if 'query' in final_state and isinstance(final_state['query'], dict):
                final_state['query'] = EcoQuery(**final_state['query'])
            final_state = AgentState(**final_state)
        
        # Convert to GaiaScoutResponse
        if final_state.response_type == "clarification":
            return GaiaScoutResponse(
                response_type="clarification",
                session_id=final_state.session_id,
                timestamp=final_state.timestamp,
                clarification=final_state.clarification_request,
                variables_used=final_state.variables_used,
                knowledge_retrieved=final_state.knowledge_retrieved,
                retrieval_sources=final_state.retrieval_sources
            )
        elif final_state.response_type == "assessment":
            return GaiaScoutResponse(
                response_type="assessment",
                session_id=final_state.session_id,
                timestamp=final_state.timestamp,
                metric_assessments=[
                    # Convert assessments to MetricAssessment format
                    # This is a simplified conversion - in production you'd want full mapping
                ] if final_state.assessments else None,
                limiting_factors=[lf.get("metric", "") for lf in final_state.limiting_factors] if final_state.limiting_factors else None,
                recommendations=final_state.recommendations,
                summary=final_state.summary,
                variables_used=final_state.variables_used,
                knowledge_retrieved=final_state.knowledge_retrieved,
                retrieval_sources=final_state.retrieval_sources
            )
        else:
            return GaiaScoutResponse(
                response_type="conversational",
                session_id=final_state.session_id,
                timestamp=final_state.timestamp,
                message=final_state.message or "I'm here to help with your environmental questions.",
                variables_used=final_state.variables_used
            )


# ─────────────────────────────────────────────────────────────
# DEMO / TESTING
# ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    # Simple demo
    from backend.models.schemas import EcoQuery, SoilMetrics
    
    # Test case: low SOC, high pH, semi-arid, monoculture
    test_query = EcoQuery(
        user_message="My farmland has poor soil health and I'm concerned about declining biodiversity.",
        soil=SoilMetrics(organic_carbon_pct=0.3, ph=8.2),
        land_use_type="cropland_monoculture",
        biome="semi_arid"
    )
    
    agent = GaiaScoutAgent()
    response = agent.invoke(test_query)
    
    print("=== GaiaScout Response ===")
    print(f"Response Type: {response.response_type}")
    print(f"Session ID: {response.session_id}")
    
    if response.response_type == "clarification":
        print(f"Clarification Needed: {response.clarification.question if response.clarification else 'None'}")
    elif response.response_type == "assessment":
        print(f"Summary: {response.summary}")
        if response.recommendations:
            print(f"Top Recommendation: {response.recommendations[0].action_title}")
            print(f"Confidence: {response.recommendations[0].confidence.value}")
    
    print("========================")