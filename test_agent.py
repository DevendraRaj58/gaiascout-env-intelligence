import sys
sys.path.append('e:\\AI_env_scientist')
from backend.agent.gaiaScout_agent import GaiaScoutAgent
from backend.models.schemas import EcoQuery, SoilMetrics

# Test case: low SOC, high pH, semi-arid, monoculture
test_query = EcoQuery(
    user_message="My farmland has poor soil health and I'm concerned about declining biodiversity.",
    soil=SoilMetrics(organic_carbon_pct=0.3, ph=8.2),
    land_use_type="cropland_monoculture",
    biome="semi_arid"
)

agent = GaiaScoutAgent()
try:
    response = agent.invoke(test_query)
    print('Success!')
    print(f'Response type: {response.response_type}')
    if response.response_type == "clarification":
        print(f'Clarification: {response.clarification.question if response.clarification else "None"}')
    elif response.response_type == "assessment":
        print(f'Summary: {response.summary}')
except Exception as e:
    print(f'Error: {e}')
    import traceback
    traceback.print_exc()