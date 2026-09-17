"""
GaiaScout FastAPI Backend — Exposes the environmental intelligence agent via HTTP.

Endpoints:
- POST /analyze — Main endpoint for environmental analysis and recommendations
- GET /health — Health check endpoint
- GET / — Root endpoint with API information

Features:
- Accepts both text and structured JSON input
- Returns structured, evidence-backed recommendations
- Supports Server-Sent Events (SSE) for streaming responses
- Handles multi-turn conversations with session management
- Provides CORS middleware for frontend integration
"""

import os
import json
from typing import Optional, List, Dict, Any
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import uvicorn
from dotenv import load_dotenv

# Import our agent and schemas
from backend.agent.gaiaScout_agent import GaiaScoutAgent
from backend.models.schemas import EcoQuery, GaiaScoutResponse

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="GaiaScout API",
    description="AI-powered environmental intelligence system for biodiversity conservation",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize the agent
agent = GaiaScoutAgent()

# In-memory session store (in production, use Redis or database)
sessions: Dict[str, Dict[str, Any]] = {}


# ─────────────────────────────────────────────────────────────
# REQUEST/RESPONSE MODELS
# ─────────────────────────────────────────────────────────────

class AnalyzeRequest(BaseModel):
    """Request model for the /analyze endpoint."""
    session_id: Optional[str] = None
    user_message: str
    # Optional structured inputs (can be provided separately)
    soil_organic_carbon_pct: Optional[float] = None
    ph: Optional[float] = None
    soil_moisture_pct: Optional[float] = None
    annual_rainfall_mm: Optional[float] = None
    mean_temperature_c: Optional[float] = None
    species_richness: Optional[int] = None
    habitat_diversity: Optional[float] = None
    deforestation_rate_pct: Optional[float] = None
    land_fragmentation: Optional[str] = None
    land_use_type: Optional[str] = None
    biome: Optional[str] = None
    crop_type: Optional[str] = None


class AnalyzeResponse(BaseModel):
    """Response model for the /analyze endpoint."""
    session_id: str
    response_type: str  # "clarification" | "assessment" | "conversational"
    timestamp: str
    # For clarification responses
    clarification: Optional[Dict[str, Any]] = None
    # For assessment responses
    summary: Optional[str] = None
    recommendations: Optional[List[Dict[str, Any]]] = None
    # Metadata
    variables_used: List[str] = []
    knowledge_retrieved: bool = False
    retrieval_sources: List[str] = []


# ─────────────────────────────────────────────────────────────
# ENDPOINTS
# ─────────────────────────────────────────────────────────────

@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "GaiaScout AI Environmental Intelligence API",
        "version": "0.1.0",
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "GaiaScout",
        "version": "0.1.0",
        "timestamp": os.environ.get("TIMESTAMP", "unknown")
    }


@app.post("/analyze", response_model=AnalyzeResponse)
async def analyze_environment(request: AnalyzeRequest):
    """
    Main endpoint for environmental analysis.
    Accepts structured input and returns evidence-backed recommendations.
    """
    # Generate or retrieve session ID
    session_id = request.session_id or os.urandom(16).hex()
    
    # Retrieve or initialize session
    if session_id not in sessions:
        sessions[session_id] = {
            "conversation_history": [],
            "created_at": os.environ.get("TIMESTAMP", "unknown")
        }
    
    session = sessions[session_id]
    
    # Build EcoQuery from request
    # Handle structured inputs
    soil_metrics = None
    if any(v is not None for v in [request.soil_organic_carbon_pct, request.ph, request.soil_moisture_pct]):
        soil_metrics = {
            "organic_carbon_pct": request.soil_organic_carbon_pct,
            "ph": request.ph,
            "moisture_pct": request.soil_moisture_pct
    }
    # Remove None values
    soil_metrics = {k: v for k, v in soil_metrics.items() if v is not None} if soil_metrics else None
    
    climate_metrics = None
    if any(v is not None for v in [request.annual_rainfall_mm, request.mean_temperature_c]):
        climate_metrics = {
            "annual_rainfall_mm": request.annual_rainfall_mm,
            "mean_temp_celsius": request.mean_temperature_c
        }
    climate_metrics = {k: v for k, v in climate_metrics.items() if v is not None} if climate_metrics else None
    
    biodiversity_metrics = None
    if any(v is not None for v in [request.species_richness, request.habitat_diversity]):
        biodiversity_metrics = {
            "species_richness": request.species_richness,
            "habitat_diversity": request.habitat_diversity
        }
    biodiversity_metrics = {k: v for k, v in biodiversity_metrics.items() if v is not None} if biodiversity_metrics else None
    
    human_impact_metrics = None
    if request.deforestation_rate_pct is not None or request.land_fragmentation is not None:
        human_impact_metrics = {
            "deforestation_rate_pct": request.deforestation_rate_pct,
            "land_fragmentation": request.land_fragmentation
        }
    human_impact_metrics = {k: v for k, v in human_impact_metrics.items() if v is not None} if human_impact_metrics else None
    
    # Create the EcoQuery
    query = EcoQuery(
        session_id=session_id,
        user_message=request.user_message,
        conversation_history=session["conversation_history"],
        soil=soil_metrics,
        biodiversity=biodiversity_metrics,
        climate=climate_metrics,
        human_impact=human_impact_metrics,
        land_use_type=request.land_use_type,
        biome=request.biome,
        crop_type=request.crop_type
    )
    
    # Process with the agent
    try:
        response = agent.invoke(query)
        
        # Update session history
        session["conversation_history"].append({
            "user": request.user_message,
            "agent": response.summary or response.message or "Clarification requested",
            "timestamp": response.timestamp
        })
        
        # Keep only last 10 exchanges to prevent memory issues
        if len(session["conversation_history"]) > 10:
            session["conversation_history"] = session["conversation_history"][-10:]
        
        # Convert response to AnalyzeResponse format
        return AnalyzeResponse(
            session_id=response.session_id,
            response_type=response.response_type,
            timestamp=response.timestamp,
            clarification=response.clarification.model_dump() if response.clarification else None,
            summary=response.summary,
            recommendations=[rec.model_dump() for rec in response.recommendations] if response.recommendations else None,
            variables_used=response.variables_used,
            knowledge_retrieved=response.knowledge_retrieved,
            retrieval_sources=response.retrieval_sources
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.post("/analyze/stream")
async def analyze_environment_stream(request: AnalyzeRequest):
    """
    Streaming endpoint for real-time responses using Server-Sent Events.
    Useful for longer processing or when you want to show intermediate steps.
    """
    # For MVP, we'll return the same as the regular endpoint but as SSE
    # In a full implementation, you'd yield intermediate steps
    
    async def event_generator():
        # Get the regular response
        response = await analyze_environment(request)
        
        # Format as SSE
        yield f"data: {json.dumps(response.model_dump())}\n\n"
        yield f"data: [DONE]\n\n"
    
    return StreamingResponse(
        event_generator(),
        media_type="text/plain",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Content-Type": "text/event-stream",
        }
    )


# ─────────────────────────────────────────────────────────────
# STARTUP/SHUTDOWN EVENTS
# ─────────────────────────────────────────────────────────────

@app.on_event("startup")
async def startup_event():
    """Initialize resources on startup."""
    print("🌱 GaiaScout API starting up...")
    print("📚 Loading environmental knowledge base...")
    print("🔗 Initializing hybrid retrieval system...")
    print("✅ GaiaScout is ready to analyze ecosystems!")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup resources on shutdown."""
    print("🌱 GaiaScout API shutting down...")
    # Close any open connections, save state, etc.


# ─────────────────────────────────────────────────────────────
# MAIN ENTRY POINT
# ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    # Get configuration from environment
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))
    
    # Run the server
    uvicorn.run(
        "backend.main:app",
        host=host,
        port=port,
        reload=True if os.getenv("ENV") == "development" else False,
        log_level="info"
    )