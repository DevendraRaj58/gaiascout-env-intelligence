"""
Test script for GaiaScout API using TestClient
"""
import sys
import os
sys.path.insert(0, os.path.abspath('.'))

from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    print("✓ Health endpoint passed")

def test_root():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    print("✓ Root endpoint passed")

def test_analyze_insufficient():
    response = client.post(
        "/analyze",
        json={"user_message": "My farmland has poor soil health and I'm concerned about declining biodiversity."}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["response_type"] == "clarification"
    assert "clarification" in data
    print("✓ Insufficient data test passed")

def test_analyze_sufficient():
    response = client.post(
        "/analyze",
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
            "land_fragmentation": "moderate",
            "land_use_type": "cropland_monoculture",
            "biome": "semi_arid"
        }
    )
    print(f"Response status: {response.status_code}")
    data = response.json()
    print(f"Response data: {data}")
    assert response.status_code == 200
    assert data["response_type"] == "assessment", f"Expected assessment, got {data['response_type']}"
    assert "summary" in data
    assert "recommendations" in data
    print("✓ Sufficient data test passed")

def test_analyze_stream():
    response = client.post(
        "/analyze/stream",
        json={
            "user_message": "Test streaming",
            "soil_organic_carbon_pct": 0.3,
            "ph": 8.2
        }
    )
    assert response.status_code == 200
    # Check that it's streaming
    assert "text/event-stream" in response.headers.get("content-type", "")
    print("✓ Streaming endpoint passed")

if __name__ == "__main__":
    print("Testing GaiaScout API with TestClient")
    print("=" * 40)
    try:
        test_health()
        test_root()
        test_analyze_insufficient()
        test_analyze_sufficient()
        test_analyze_stream()
        print("\n" + "=" * 40)
        print("All API tests passed!")
    except Exception as e:
        print(f"\nTest failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)