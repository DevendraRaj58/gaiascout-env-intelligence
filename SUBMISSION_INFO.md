# Submission Information for Darukaa.Earth AI Biodiversity Intelligence Chatbot

## 1. GitHub Repository Link
[To be filled by the user after creating the repository]
Example: https://github.com/your-username/gaiascout-env-intelligence

## 2. Live Demo URL
[To be filled by the user after deployment]
Example: https://gaiascout-env-intelligence.vercel.app

## 3. README.md Overview
Please refer to the README.md file in the root of this repository for a comprehensive overview covering:
- Architecture
- Knowledge System (database/schema)
- Local setup instructions
- CI/CD details (if applicable)

## 4. Additional Links, Credentials, and Notes

### Backend API Documentation
When running locally, the API documentation is available at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Frontend Development
When running locally, the frontend is available at:
- http://localhost:3000

### Environment Variables
The backend requires a `.env` file. A template is provided in `.env.example`.
Key variables include:
- `OPENAI_API_KEY` (optional, for using OpenAI LLMs)
- `HUGGINGFACE_API_KEY` (optional, for using Hugging Face models)
- Other API keys for external services if needed

### Deployment Instructions
#### Backend (Render.com)
1. Create a new Web Service
2. Connect to your GitHub repository
3. Set build command: `pip install -r backend/requirements.txt`
4. Set start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
5. Add environment variables from your `.env` file

#### Frontend (Vercel)
1. Import your GitHub repository
2. Vercel will automatically detect the frontend directory
3. Set build command: `npm run build`
4. Set output directory: `build`
5. Add environment variables if needed

### Running Locally
1. Clone the repository
2. Backend:
   - `cd backend`
   - `python -m venv .venv`
   - `.venv\Scripts\activate` (Windows) or `source .venv/bin/activate` (Linux/Mac)
   - `pip install -r requirements.txt`
   - `cp .env.example .env` (and edit if needed)
   - `uvicorn main:app --reload`
3. Frontend:
   - `cd frontend`
   - `npm install`
   - `npm start`

### Test Credentials
For testing purposes, you can use the following example input:
```json
{
  "user_message": "My farmland has poor soil health and I'm concerned about declining biodiversity.",
  "soil": {
    "organic_carbon_pct": 0.3,
    "ph": 8.2
  },
  "land_use_type": "cropland_monoculture",
  "biome": "semi_arid"
}
```
This should trigger a clarification request for missing human impact data, or if you provide more data, it will generate evidence-backed recommendations.

### Notes
- The system is designed to work without external API keys for the MVP (using local embeddings and rule-based reasoning).
- For enhanced LLM capabilities, you can add an OpenAI or Hugging Face API key to the `.env` file.
- The knowledge base (SQLite and ChromaDB) is initialized by running `python backend/knowledge/ingestion.py` (already done in the provided database files).