import sys
sys.path.append('e:\\AI_env_scientist')
from backend.agent.gaiaScout_agent import GaiaScoutAgent
from backend.models.schemas import EcoQuery, SoilMetrics, BiodiversityMetrics, ClimateMetrics, HumanImpactMetrics, BiomeType, LandUseType

# Test case with sufficient data: low SOC, high pH, semi-arid, monoculture, but with additional metrics
test_query = EcoQuery(
    user_message="My farmland has poor soil health (low SOC, high pH) and I'm concerned about declining biodiversity in a semi-arid region with monoculture farming.",
    soil=SoilMetrics(organic_carbon_pct=0.3, ph=8.2, moisture_pct=0.15),
    biodiversity=BiodiversityMetrics(species_richness=12, habitat_diversity=0.4, pollinator_abundance="moderate"),
    climate=ClimateMetrics(annual_rainfall_mm=350, mean_temp_celsius=22, drought_frequency="occasional"),
    human_impact=HumanImpactMetrics(deforestation_rate_pct=0.02, pollution_level="moderate", pesticide_use="low", land_fragmentation="moderate"),
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
        if response.recommendations:
            print(f"Number of recommendations: {len(response.recommendations)}")
            for i, rec in enumerate(response.recommendations):
                print(f"  Recommendation {i+1}: {rec.action_title}")
                print(f"    Confidence: {rec.confidence.value}")
                print(f"    Time horizon: {rec.time_horizon.value}")
except Exception as e:
    print(f'Error: {e}')
    import traceback
    traceback.print_exc()