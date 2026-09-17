from backend.engine.missing_variable import MissingVariableDetector

detector = MissingVariableDetector()

# Simulate the provided_metrics after the conversion in missing_variable_check_node
provided_metrics = {
    "organic_carbon_pct": 0.3,
    "ph": 8.2,
    "moisture_pct": 0.15,
    "species_richness": 12,
    "habitat_diversity": 0.4,
    "annual_rainfall_mm": 350,
    "mean_temp_celsius": 22,
    "deforestation_rate_pct": 0.02,
    "land_fragmentation": "moderate"
}

print("Provided metrics:", provided_metrics)
result = detector.detect(provided_metrics)
print("Detection result:", result)