import subprocess
import time
import requests
import json
import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.abspath('.'))

def test_agent():
    """Test the agent directly"""
    print("=" * 50)
    print("Testing Agent Directly")
    print("=" * 50)
    
    from backend.agent.gaiaScout_agent import GaiaScoutAgent
    from backend.models.schemas import EcoQuery, SoilMetrics, BiodiversityMetrics, ClimateMetrics, HumanImpactMetrics, LandUseType, BiomeType
    
    # Test insufficient data
    print("\n1. Testing insufficient data...")
    insufficient_query = EcoQuery(
        user_message="My farmland has poor soil health and I'm concerned about declining biodiversity.",
        soil=SoilMetrics(organic_carbon_pct=0.3, ph=8.2),
        land_use_type="cropland_monoculture",
        biome="semi_arid"
    )
    
    agent = GaiaScoutAgent()
    response = agent.invoke(insufficient_query)
    print(f"   Response type: {response.response_type}")
    assert response.response_type == "clarification", f"Expected clarification, got {response.response_type}"
    print("   ✓ Correctly requested clarification")
    
    # Test sufficient data
    print("\n2. Testing sufficient data...")
    sufficient_query = EcoQuery(
        user_message="My farmland has poor soil health (low SOC, high pH) and I'm concerned about declining biodiversity in a semi-arid region with monoculture farming.",
        soil=SoilMetrics(organic_carbon_pct=0.3, ph=8.2, moisture_pct=0.15),
        biodiversity=BiodiversityMetrics(species_richness=12, habitat_diversity=0.4, pollinator_abundance="moderate"),
        climate=ClimateMetrics(annual_rainfall_mm=350, mean_temp_celsius=22, drought_frequency="occasional"),
        human_impact=HumanImpactMetrics(deforestation_rate_pct=0.02, pollution_level="moderate", pesticide_use="low", land_fragmentation="moderate"),
        land_use_type="cropland_monoculture",
        biome="semi_arid"
    )
    
    response = agent.invoke(sufficient_query)
    print(f"   Response type: {response.response_type}")
    assert response.response_type == "assessment", f"Expected assessment, got {response.response_type}"
    print("   ✓ Returned assessment")
    print(f"   Summary: {response.summary}")
    if response.recommendations:
        print(f"   Number of recommendations: {len(response.recommendations)}")
        for i, rec in enumerate(response.recommendations[:2]):  # Show first two
            print(f"     {i+1}. {rec.action_title} ({rec.confidence.value} confidence)")
    
    print("\n✓ Agent tests passed!")

def test_api():
    """Test the API endpoints"""
    print("\n" + "=" * 50)
    print("Testing API Endpoints")
    print("=" * 50)
    
    base_url = "http://localhost:8000"
    
    # Test health endpoint
    print("\n1. Testing health endpoint...")
    try:
        response = requests.get(f"{base_url}/health")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"
        print("   ✓ Health endpoint works")
    except Exception as e:
        print(f"   ✗ Health endpoint failed: {e}")
        return False
    
    # Test root endpoint
    print("\n2. Testing root endpoint...")
    try:
        response = requests.get(f"{base_url}/")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
        assert response.status_code == 200
        print("   ✓ Root endpoint works")
    except Exception as e:
        print(f"   ✗ Root endpoint failed: {e}")
        return False
    
    # Test analyze endpoint with insufficient data
    print("\n3. Testing /analyze with insufficient data...")
    try:
        response = requests.post(
            f"{base_url}/analyze",
            headers={"Content-Type": "application/json"},
            json={"user_message": "My farmland has poor soil health and I'm concerned about declining biodiversity."}
        )
        print(f"   Status: {response.status_code}")
        data = response.json()
        print(f"   Response type: {data.get('response_type')}")
        assert response.status_code == 200
        assert data["response_type"] == "clarification"
        assert "clarification" in data
        print("   ✓ Correctly returned clarification")
    except Exception as e:
        print(f"   ✗ Insufficient data test failed: {e}")
        return False
    
    # Test analyze endpoint with sufficient data
    print("\n4. Testing /analyze with sufficient data...")
    try:
        response = requests.post(
            f"{base_url}/analyze",
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
        print(f"   Status: {response.status_code}")
        data = response.json()
        print(f"   Response type: {data.get('response_type')}")
        assert response.status_code == 200
        assert data["response_type"] == "assessment"
        assert "summary" in data
        assert "recommendations" in data
        print("   ✓ Correctly returned assessment")
        print(f"   Summary: {data['summary'][:100]}...")
        if data["recommendations"]:
            print(f"   Number of recommendations: {len(data['recommendations'])}")
    except Exception as e:
        print(f"   ✗ Sufficient data test failed: {e}")
        return False
    
    # Test streaming endpoint
    print("\n5. Testing /analyze/stream endpoint...")
    try:
        response = requests.post(
            f"{base_url}/analyze/stream",
            headers={"Content-Type": "application/json"},
            json={
                "user_message": "Test streaming",
                "soil_organic_carbon_pct": 0.3,
                "ph": 8.2
            },
            stream=True
        )
        print(f"   Status: {response.status_code}")
        assert response.status_code == 200
        # Read the streaming response
        content = ""
        for line in response.iter_lines():
            if line:
                content += line.decode('utf-8')
                if "[DONE]" in content:
                    break
        print("   ✓ Streaming endpoint works")
        print(f"   Received: {content[:100]}...")
    except Exception as e:
        print(f"   ✗ Streaming test failed: {e}")
        return False
    
    print("\n✓ All API tests passed!")
    return True

def main():
    # First test the agent directly
    test_agent()
    
    # Start the server
    print("\n" + "=" * 50)
    print("Starting FastAPI Server")
    print("=" * 50)
    server_process = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    # Wait for server to start
    print("Waiting for server to start...")
    time.sleep(5)
    
    # Check if server is running
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            print("Server is running!")
        else:
            print("Server may not be ready yet.")
            # Try a few more times
            for i in range(3):
                time.sleep(2)
                response = requests.get("http://localhost:8000/health", timeout=5)
                if response.status_code == 200:
                    print("Server is running after retry!")
                    break
            else:
                print("Server failed to start properly.")
                # Print server output for debugging
                stdout, stderr = server_process.communicate()
                print("Server stdout:", stdout.decode())
                print("Server stderr:", stderr.decode())
                return
    except Exception as e:
        print(f"Error checking server: {e}")
        # Print server output for debugging
        stdout, stderr = server_process.communicate()
        print("Server stdout:", stdout.decode())
        print("Server stderr:", stderr.decode())
        return
    
    # Test the API
    api_success = test_api()
    
    # Stop the server
    print("\nStopping server...")
    server_process.terminate()
    server_process.wait()
    print("Server stopped.")
    
    if api_success:
        print("\n" + "=" * 50)
        print("ALL TESTS PASSED!")
        print("=" * 50)
    else:
        print("\n" + "=" * 50)
        print("SOME TESTS FAILED!")
        print("=" * 50)
        sys.exit(1)

if __name__ == "__main__":
    main()