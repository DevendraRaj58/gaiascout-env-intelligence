from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

print("Testing health endpoint...")
response = client.get("/health")
print(f"Status: {response.status_code}")
print(f"Response: {response.json()}")