import React, { useState } from 'react';
import axios from 'axios';
import './App.css';

function App() {
  const [formData, setFormData] = useState({
    user_message: '',
    soil_organic_carbon_pct: '',
    ph: '',
    soil_moisture_pct: '',
    annual_rainfall_mm: '',
    mean_temperature_c: '',
    species_richness: '',
    habitat_diversity: '',
    deforestation_rate_pct: '',
    land_fragmentation: '',
    land_use_type: '',
    biome: '',
    crop_type: ''
  });

  const [response, setResponse] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value === '' ? null : (prev[name] !== '' && !isNaN(parseFloat(value))) ? parseFloat(value) : value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      // Convert empty strings to null for numeric fields
      const payload = {};
      Object.keys(formData).forEach(key => {
        if (formData[key] !== '' && formData[key] !== null) {
          payload[key] = formData[key];
        }
      });
      const res = await axios.post('http://localhost:8000/analyze', payload);
      setResponse(res.data);
    } catch (err) {
      setError(err.response ? err.response.data : err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleStreamClick = async () => {
    setLoading(true);
    setError(null);
    try {
      const payload = {};
      Object.keys(formData).forEach(key => {
        if (formData[key] !== '' && formData[key] !== null) {
          payload[key] = formData[key];
        }
      });
      const res = await axios.post('http://localhost:8000/analyze/stream', payload, {
        responseType: 'stream'
      });
      // For simplicity, we'll just collect the data and show the last message
      let data = '';
      res.data.on('data', chunk => {
        data += chunk.toString();
        if (chunk.toString().includes('[DONE]')) {
          try {
            const jsonData = JSON.parse(data.split('\n').filter(line => line.startsWith('data: '))[0].substring(6));
            setResponse(jsonData);
          } catch (parseErr) {
            setError('Error parsing stream');
          }
        }
      });
    } catch (err) {
      setError(err.response ? err.response.data : err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>GaiaScout: Environmental Intelligence System</h1>
        <p>Get scientifically-grounded recommendations for biodiversity improvement</p>
      </header>
      <main>
        <form onSubmit={handleSubmit} className="input-form">
          <div className="form-group">
            <label htmlFor="user_message">Your Question or Concern:</label>
            <textarea
              id="user_message"
              name="user_message"
              value={formData.user_message || ''}
              onChange={handleChange}
              rows="3"
              placeholder="Describe your land, ecosystem, or environmental concern..."
              required
            />
          </div>

          <div className="metrics-grid">
            {/* Soil Metrics */}
            <section className="metric-section">
              <h2>Soil Health</h2>
              <div className="metric-field">
                <label>Organic Carbon % (SOC):</label>
                <input
                  type="number"
                  step="0.1"
                  name="soil_organic_carbon_pct"
                  value={formData.soil_organic_carbon_pct || ''}
                  onChange={handleChange}
                  placeholder="e.g., 0.3 for 0.3%"
                />
              </div>
              <div className="metric-field">
                <label>pH:</label>
                <input
                  type="number"
                  step="0.1"
                  name="ph"
                  value={formData.ph || ''}
                  onChange={handleChange}
                  placeholder="e.g., 8.2"
                />
              </div>
              <div className="metric-field">
                <label>Moisture %:</label>
                <input
                  type="number"
                  step="0.1"
                  name="soil_moisture_pct"
                  value={formData.soil_moisture_pct || ''}
                  onChange={handleChange}
                  placeholder="e.g., 0.15 for 15%"
                />
              </div>
            </section>

            {/* Biodiversity Metrics */}
            <section className="metric-section">
              <h2>Biodiversity</h2>
              <div className="metric-field">
                <label>Species Richness:</label>
                <input
                  type="number"
                  name="species_richness"
                  value={formData.species_richness || ''}
                  onChange={handleChange}
                  placeholder="Number of species"
                />
              </div>
              <div className="metric-field">
                <label>Habitat Diversity (0-1):</label>
                <input
                  type="number"
                  step="0.01"
                  min="0"
                  max="1"
                  name="habitat_diversity"
                  value={formData.habitat_diversity || ''}
                  onChange={handleChange}
                  placeholder="e.g., 0.4"
                />
              </div>
            </section>

            {/* Climate Metrics */}
            <section className="metric-section">
              <h2>Climate</h2>
              <div className="metric-field">
                <label>Annual Rainfall (mm):</label>
                <input
                  type="number"
                  name="annual_rainfall_mm"
                  value={formData.annual_rainfall_mm || ''}
                  onChange={handleChange}
                  placeholder="e.g., 350"
                />
              </div>
              <div className="metric-field">
                <label>Mean Temperature (°C):</label>
                <input
                  type="number"
                  step="0.1"
                  name="mean_temperature_c"
                  value={formData.mean_temperature_c || ''}
                  onChange={handleChange}
                  placeholder="e.g., 22"
                />
              </div>
            </section>

            {/* Human Impact Metrics */}
            <section className="metric-section">
              <h2>Human Impact</h2>
              <div className="metric-field">
                <label>Deforestation Rate (%/year):</label>
                <input
                  type="number"
                  step="0.01"
                  name="deforestation_rate_pct"
                  value={formData.deforestation_rate_pct || ''}
                  onChange={handleChange}
                  placeholder="e.g., 0.02 for 2%"
                />
              </div>
              <div className="metric-field">
                <label>Land Fragmentation:</label>
                <select name="land_fragmentation" value={formData.land_fragmentation || ''} onChange={handleChange}>
                  <option value="">Select fragmentation level</option>
                  <option value="low">Low</option>
                  <option value="moderate">Moderate</option>
                  <option value="high">High</option>
                </select>
              </div>
            </section>

            {/* Land Use & Biome */}
            <section className="metric-section">
              <h2>Land Use & Biome</h2>
              <div className="metric-field">
                <label>Land Use Type:</label>
                <select name="land_use_type" value={formData.land_use_type || ''} onChange={handleChange}>
                  <option value="">Select land use type</option>
                  <option value="cropland_monoculture">Cropland (Monoculture)</option>
                  <option value="cropland_polyculture">Cropland (Polyculture)</option>
                  <option value="pasture">Pasture</option>
                  <option value="forest">Forest</option>
                  <option value="wetland">Wetland</option>
                  <option value="urban">Urban</option>
                </select>
              </div>
              <div className="metric-field">
                <label>Biome:</label>
                <select name="biome" value={formData.biome || ''} onChange={handleChange}>
                  <option value="">Select biome</option>
                  <option value="semi_arid">Semi-arid</option>
                  <option value="temperate">Temperate</option>
                  <option value="tropical">Tropical</option>
                  <option value="boreal">Boreal</option>
                  <option value="mediterranean">Mediterranean</option>
                </select>
              </div>
              <div className="metric-field">
                <label>Crop Type (if applicable):</label>
                <input
                  type="text"
                  name="crop_type"
                  value={formData.crop_type || ''}
                  onChange={handleChange}
                  placeholder="e.g., corn, wheat, soybeans"
                />
              </div>
            </section>
          </div>

          <div className="form-actions">
            <button type="submit" disabled={loading}>
              {loading ? 'Analyzing...' : 'Get Recommendations'}
            </button>
            <button type="button" onClick={handleStreamClick} disabled={loading} className="secondary">
              {loading ? 'Streaming...' : 'Get Streaming Response'}
            </button>
          </div>
        </form>

        {error && (
          <div className="error-message">
            <h3>Error:</h3>
            <p>{error}</p>
          </div>
        )}

        {response && (
          <div className="response-section">
            <h2>Response</h2>
            {response.response_type === 'clarification' && (
              <div className="clarification">
                <h3>Clarification Needed</h3>
                <p>{response.clarification.question}</p>
                <p><em>Why needed:</em> {response.clarification.why_needed}</p>
              </div>
            )}
            {response.response_type === 'assessment' && (
              <>
                <div className="summary">
                  <h3>Assessment Summary</h3>
                  <p>{response.summary}</p>
                </div>
                {response.recommendations && response.recommendations.length > 0 && (
                  <div className="recommendations">
                    <h3>Recommendations</h3>
                    <ol>
                      {response.recommendations.map((rec, index) => (
                        <li key={rec.rank} className="recommendation-item">
                          <h4>#{rec.rank}: {rec.action_title}</h4>
                          <p>{rec.action_description}</p>
                          <div className="rec-details">
                            <span><strong>Mechanism:</strong> {rec.mechanism}</span>
                            <span><strong>Limiting Factor:</strong> {rec.limiting_factor}</span>
                            <span><strong>Time Horizon:</strong> {rec.time_horizon}</span>
                            <span><strong>Confidence:</strong> {rec.confidence}</span>
                          </div>
                          {rec.metric_impacts && rec.metric_impacts.length > 0 && (
                            <div className="metric-impacts">
                              <h5>Expected Impacts:</h5>
                              <ul>
                                {rec.metric_impacts.map(impact => (
                                  <li key={impact.metric_name}>
                                    <strong>{impact.metric_name}:</strong> 
                                    {impact.expected_change} 
                                    {(impact.current_severity !== null && ` (current: ${impact.current_severity})`) || ''}
                                  </li>
                                ))}
                              </ul>
                            </div>
                          )}
                          {rec.implementation_steps && rec.implementation_steps.length > 0 && (
                            <div className="implementation-steps">
                              <h5>Implementation Steps:</h5>
                              <ol>
                                {rec.implementation_steps.map((step, idx) => (
                                  <li key={idx}>{step}</li>
                                ))}
                              </ol>
                            </div>
                          )}
                          {rec.retrieved_chunks && rec.retrieved_chunks.length > 0 && (
                            <div className="retrieved-chunks">
                              <h5>Scientific Evidence:</h5>
                              {rec.retrieved_chunks.map((chunk, idx) => (
                                <div key={idx} className="chunk">
                                  <p>{chunk}</p>
                                </div>
                              ))}
                            </div>
                          )}
                        </li>
                      ))}
                    </ol>
                  </div>
                )}
              </>
            )}
          </div>
        )}
      </main>
    </div>
  );
}

export default App;