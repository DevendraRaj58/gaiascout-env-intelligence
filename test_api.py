import requests
import json

# Test health endpoint
print("Testing health endpoint...")
try:
    response = requests.get("http://localhost:8000/health")
    print(f"Health check: {response.status_code}")
    print(f"Response: {response.json()}")
except Exception as e:
    print(f"Health check failed: {e}")

# Test root endpoint
print("\nTesting root endpoint...")
try:
    response = requests.get("http://localhost:8000/")
    print(f"Root endpoint: {response.status_code}")
    print(f"Response: {response.json()}")
except Exception as e:
    print(f"Root endpoint failed: {e}")

# Test analyze endpoint with insufficient data
print("\nTesting /analyze with insufficient data...")
try:
    response = requests.post(
        "http://localhost:8000/analyze",
        headers={"Content-Type": "application/json"},
        json={"user_message": "My farmland has poor soil health and I'm concerned about declining biodiversity."}
    )
    print(f"Insufficient data test: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
except Exception as e:
    print(f"Insufficient data test failed: {e}")

# Test analyze endpoint with sufficient data
print("\nTesting /analyze with sufficient data...")
try:
    response = requests.post(
        "http://localhost:8000/analyze",
        headers={"Content-Type": "application/json"},
        json={
            "user_message": "My farmland has poor soil health (low SOC, high pH) and I'm concerned about declining biodiversity in a semi-arid region with monoculture farming.",
            "soil_organic_carbon_pct": 0.3,
            "ph": 8.2,
            "soil_moisture_pct": 0.15,
            "annual_rainfall_mm": 350,
            "mean_temperature_c": 22,
            "species_richness": 12,
            "habitat_diversity": 0.4,
            "deforestation_rate_pct": 0.02,
            "land_use_type": "cropland_monoculture",
            "biome": "semi_arid"
        }
    )
    print(f"Sufficient data test: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
except Exception as e:
    print(f"Sufficient data test failed: {e}")

# Test streaming endpoint
print("\nTesting /analyze/stream endpoint...")
try:
    response = requests.post(
        "http://localhost:8000/analyze/stream",
        headers={"Content-Type": "application/json"},
        json={
            "user_message": "My farmland has poor soil health (low SOC, high pH) and I'm concerned about declining biodiversity in a semi-arid region with monoculture farming.",
            "soil_organic_carbon_pct": 0.3,
            "ph": 8.2,
            "soil_moisture_pct": 0.15,
            "annual_rainfall_mm": 350,
            "mean_temperature_c": 22,
            "species_richness": 12,
            "habitat_diversity": 0.4,
            "deforestation_rate_pct": 0.02,
            "land_use_type": "cropland_monoculture",
            "biome": "semi_arid"
        },
        stream=True
    )
    print(f"Streaming test: {response.status_code}")
    print("Streaming response:")
    for line in response.iter_lines():
        if line:
            print(f"  {line.decode('utf-8')}")
except Exception as e:
    print(f"Streaming test failed: {e}")