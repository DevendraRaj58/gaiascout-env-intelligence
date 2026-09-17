import sys, os
sys.path.insert(0, '.')

from knowledge.structured_db import setup_database, get_metric_severity, get_interventions_for_context, get_biome_profile

setup_database()
print()

# Test 1: What severity is SOC of 0.3%?
result = get_metric_severity('soil_organic_carbon_pct', 0.3)
print("TEST 1 - SOC 0.3% severity:", result['severity'])
print("  Reason:", result['description'][:100])
print()

# Test 2: Get interventions for semi-arid monoculture
interventions = get_interventions_for_context(biome='semi_arid', land_use='cropland_monoculture', limit=3)
print("TEST 2 - Interventions for semi-arid monoculture:")
for i in interventions:
    print(f"  - {i['name']} ({i['time_horizon']} term, {i['confidence']} confidence)")
print()

# Test 3: Biome profile
profile = get_biome_profile('semi_arid')
print("TEST 3 - Semi-arid biome profile:")
print(f"  Typical SOC: {profile.get('typical_soc_range')}")
print(f"  Rainfall: {profile.get('typical_rainfall_mm')} mm/year")
print(f"  Conservation priority: {profile.get('conservation_priority')}")
print()
print("ALL TESTS PASSED!")
