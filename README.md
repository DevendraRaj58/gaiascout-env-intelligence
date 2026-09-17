# Darukaa.Earth: AI Biodiversity Intelligence Chatbot

GaiaScout is an AI-powered conversational system designed for the Darukaa.Earth Hackathon. It maintains a structured knowledge base of biodiversity and environmental metrics, understands user queries about ecosystems, and generates actionable, evidence-backed recommendations to improve biodiversity.

## Table of Contents
- [Overview](#overview)
- [Architecture](#architecture)
- [Knowledge System](#knowledge-system)
- [Setup Instructions](#setup-instructions)
- [Running the Application](#running-the-application)
- [API Endpoints](#api-endpoints)
- [Data Models](#data-models)
- [Future Work](#future-work)
- [Deployment](#deployment)

## Overview

GaiaScout implements an environmental intelligence agent that:
1. Accepts user input (text or structured JSON) about land conditions
2. Checks for sufficient data across multiple environmental domains (soil, biodiversity, climate, human impact)
3. If data is insufficient, asks clarifying questions to gather missing metrics
4. If data is sufficient, runs deterministic environmental reasoning to assess metric health and identify limiting factors
5. Retrieves relevant scientific evidence from a hybrid knowledge base (ChromaDB + SQLite)
6. Generates structured, evidence-backed recommendations with scientific references
7. Supports multi-turn conversations with session memory

## Architecture

```mermaid
graph TD
    A[User Input] --> B(FastAPI Backend)
    B --> C[GaiaScout LangGraph Agent]
    C --> D{Understand Node}
    D --> E[Missing Variable Check]
    E -->|Insufficient Data| F[Clarification Request]
    E -->|Sufficient Data| G[EcoMetric Engine]
    G --> H[Limiting Factors & Stress Score]
    H --> I[Knowledge Retrieval (ChromaDB + BM25)]
    I --> J[Reasoning Node]
    J --> K[Generate Evidence-Backed Recommendations]
    K --> L[Response Formatting]
    L --> M[User Response]
    M -->|Conversation History| N[Session Memory]
    N -->|Context| D
```

### Components

1. **FastAPI Backend** (`backend/main.py`)
   - REST API endpoints for environmental analysis
   - CORS middleware for frontend integration
   - Server-Sent Events (SSE) support for streaming responses

2. **GaiaScout LangGraph Agent** (`backend/agent/gaiaScout_agent.py`)
   - Stateful conversation flow with checkpoints
   - Conditional routing (clarify vs recommend)
   - Multi-turn conversation memory

3. **Environmental Reasoning Engine** (`backend/engine/eco_metric_engine.py`)
   - Deterministic assessment of metric severity using SQLite thresholds
   - Environmental stress score calculation (weighted average of metric severities)
   - Limiting factor identification (Liebig's law of the minimum)
   - Intervention candidate retrieval from SQLite

4. **Knowledge System**
   - **Structured Data Layer** (SQLite): Numeric thresholds, intervention metadata, biome profiles
   - **Semantic Search Layer** (ChromaDB + BM25): Retrieval of scientific text chunks for evidence

5. **Frontend** (`frontend/`)
   - React.js interface for user interaction
   - Real-time chat with session persistence

## Knowledge System

### Structured Data (SQLite)

The SQLite database (`data/gaiaScout.db`) contains four tables:

1. `metric_thresholds`: Defines critical/poor/moderate/good/excellent ranges for each environmental metric
   - Example: Soil organic carbon < 0.5% → "critical", 0.5-1.0% → "poor", etc.

2. `ecosystem_interventions`: Curated, citable interventions with full metadata
   - Includes: mechanism, action description, implementation steps, quantified impacts, time horizon, confidence level, scientific references

3. `biome_profiles`: Default baselines for each biome type (typical SOC, pH, rainfall ranges)

4. `study_refs`: Full citation records for scientific references

### Semantic Search (ChromaDB + BM25)

- **ChromaDB**: Stores embeddings of scientific text chunks (from IPCC reports, FAO studies, etc.) for semantic similarity search
- **BM25**: Keyword-based search for exact term matching
- **Hybrid Retrieval**: Combines both approaches for optimal relevance

## Setup Instructions

### Prerequisites

- Python 3.10+
- Node.js 16+
- Git

### Backend Setup

1. Clone the repository
2. Create a virtual environment:
   ```bash
   python -m venv .venv
   .venv\Scripts\activate  # Windows
   source .venv/bin/activate  # Linux/Mac
   ```
3. Install dependencies:
   ```bash
   pip install -r backend/requirements.txt
   ```
4. Set up environment variables:
   ```bash
   cp .env.example .env
   # Edit .env to add API keys if using external LLMs (optional for MVP)
   ```
5. Initialize the knowledge base (run once):
   ```bash
   python backend/knowledge/ingestion.py
   ```

### Frontend Setup

1. Navigate to frontend directory:
   ```bash
   cd frontend
   ```
2. Install dependencies:
   ```bash
   npm install
   ```
3. Start the development server:
   ```bash
   npm start
   ```

## Running the Application

1. Start the backend server:
   ```bash
   cd backend
   uvicorn main:app --reload
   ```
2. Start the frontend (in another terminal):
   ```bash
   cd frontend
   npm start
   ```
3. Open your browser to `http://localhost:3000`

### Example Usage

Try asking: "My farmland has poor soil health and I'm concerned about declining biodiversity."

The system will:
1. Detect missing variables (if any) and ask clarifying questions
2. Or, if sufficient data is provided in subsequent turns, generate evidence-backed recommendations

## API Endpoints

### POST `/analyze`
Main endpoint for environmental analysis and recommendations.

**Request Body:**
```json
{
  "user_message": "My farmland has poor soil health",
  "soil": {
    "organic_carbon_pct": 0.3,
    "ph": 8.2
  },
  "land_use_type": "cropland_monoculture",
  "biome": "semi_arid"
}
```

**Response:**
```json
{
  "response_type": "assessment",
  "session_id": "uuid-string",
  "timestamp": "2026-09-18T10:00:00Z",
  "summary": "Based on your environmental metrics showing 16.1% stress, I recommend legume-based cover cropping...",
  "recommendations": [
    {
      "rank": 1,
      "action_title": "Legume-Based Cover Cropping",
      "action_description": "Plant legume cover crops...",
      "mechanism": "Legumes fix atmospheric nitrogen...",
      "limiting_factor": "habitat_diversity",
      "metric_impacts": [
        {
          "metric_name": "Soil Organic Carbon",
          "expected_change": "+15–25% over 3 years",
          "improvement_after": "MODERATE"
        }
      ],
      "time_horizon": "medium",
      "confidence": "high",
      "references": [
        {
          "title": "FAO Soil Organic Carbon Sequestration",
          "organization": "FAO",
          "year": 2020,
          "key_finding": "Cover crops can increase SOC by 15-25% over 2-3 years"
        }
      ],
      "retrieved_chunks": [
        "Text chunk from knowledge base about cover crops..."
      ],
      "implementation_steps": [
        "1. Select appropriate legume species for your region",
        "2. Plant between main crop cycles or as inter-row strips",
        "3. Terminate and incorporate before seed set"
      ]
    }
  ],
  "variables_used": ["soil_ph", "soil_organic_carbon_pct", ...],
  "knowledge_retrieved": true,
  "retrieval_sources": ["FAO_2020_Soil_Biodiversity.pdf", ...]
}
```

### GET `/health`
Health check endpoint.

### GET `/`
Root endpoint with API information.

## Data Models

All data models are defined using Pydantic in `backend/models/schemas.py`:

### Input Models
- `EcoQuery`: Main input model containing all possible user-provided metrics
- Domain-specific models: `SoilMetrics`, `BiodiversityMetrics`, `ClimateMetrics`, `HumanImpactMetrics`
- `GeoContext`: Optional geographical coordinates for biome inference

### Output Models
- `GaiaScoutResponse`: Complete response envelope
- `EcoRecommendation`: Single structured recommendation with evidence
- `MetricImpact`: Quantified impact on a specific environmental metric
- `ScientificReference`: Citable scientific source
- `MissingVariableRequest`: Structured clarification request

## Future Work

1. **LLM Integration**: Replace rule-based reasoning with LLM for more nuanced recommendations while maintaining knowledge grounding
2. **Spatial Analysis**: Integrate GIS data for location-specific recommendations
3. **Temporal Dynamics**: Model long-term ecosystem changes under different intervention scenarios
4. **User Feedback Loop**: Incorporate user outcomes to improve recommendation accuracy
5. **Multi-Language Support**: Expand to serve global users

## Deployment

### Backend (Render.com)
1. Create a new Web Service
2. Connect to your GitHub repository
3. Set build command: `pip install -r backend/requirements.txt`
4. Set start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
5. Add environment variables from `.env`

### Frontend (Vercel)
1. Import your GitHub repository
2. Vercel will automatically detect the frontend directory
3. Set build command: `npm run build`
4. Set output directory: `build`
5. Add environment variables if needed

### Docker Deployment
Dockerfiles are provided for both backend and frontend for containerized deployment.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Darukaa.Earth for the hackathon challenge
- Open-source projects: FastAPI, LangGraph, ChromaDB, Sentence Transformers, React