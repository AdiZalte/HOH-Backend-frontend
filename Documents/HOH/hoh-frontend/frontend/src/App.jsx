import { useState } from 'react'
import './App.css'

function App() {
  const [customerId, setCustomerId] = useState('')
  const [customerData, setCustomerData] = useState(null)
  const [explanation, setExplanation] = useState(null)
  const [loading, setLoading] = useState(false)
  const [loadingExplanation, setLoadingExplanation] = useState(false)
  const [error, setError] = useState(null)

  const handleSearch = (e) => {
    e.preventDefault();
    if (!customerId) return;

    setLoading(true);
    setError(null);
    setCustomerData(null);
    setExplanation(null);

    fetch(`/api/customer/${customerId}`)
      .then(res => {
        if (!res.ok) {
          if (res.status === 404) throw new Error('Customer ID not found');
          throw new Error('Failed to fetch customer data');
        }
        return res.json()
      })
      .then(data => {
        setCustomerData(data)
        setLoading(false)
        // Automatically fetch explanation
        fetchExplanation(customerId);
      })
      .catch(err => {
        setError(err.message)
        setLoading(false)
      })
  }

  const fetchExplanation = (id) => {
    setLoadingExplanation(true);

    fetch(`/api/customer/${id}/explain`)
      .then(res => {
        if (!res.ok) {
          throw new Error('Failed to fetch explanation');
        }
        return res.json()
      })
      .then(data => {
        setExplanation(data.explanation)
        setLoadingExplanation(false)
      })
      .catch(err => {
        console.error('Explanation error:', err)
        setLoadingExplanation(false)
      })
  }

  const renderExplanation = () => {
    if (!explanation) return null;

    const { shap_values, feature_names, base_value } = explanation;

    // Create array of {name, value, featureValue} and sort by absolute SHAP value
    const features = feature_names.map((name, idx) => ({
      name: name,
      value: shap_values[idx],
      featureValue: explanation.feature_values[idx]
    })).sort((a, b) => Math.abs(b.value) - Math.abs(a.value));

    // Get max absolute value for scaling
    const maxAbsValue = Math.max(...features.map(f => Math.abs(f.value)));

    return (
      <div className="explanation-card">
        <h2>SHAP Explanation</h2>
        <p style={{ fontSize: '14px', color: '#666', marginBottom: '20px' }}>
          How each feature contributes to the risk score
        </p>

        <div className="shap-chart">
          {features.map((feature, idx) => {
            const isPositive = feature.value > 0;
            const barWidth = (Math.abs(feature.value) / maxAbsValue) * 100;

            return (
              <div key={idx} className="shap-feature-row">
                <div className="feature-info">
                  <span className="feature-name">{feature.name}</span>
                  <span className="feature-value">= {feature.featureValue.toFixed(2)}</span>
                </div>
                <div className="shap-bar-container">
                  <div
                    className={`shap-bar ${isPositive ? 'positive' : 'negative'}`}
                    style={{ width: `${barWidth}%` }}
                  >
                    <span className="shap-value">
                      {isPositive ? '+' : ''}{feature.value.toFixed(4)}
                    </span>
                  </div>
                </div>
              </div>
            );
          })}
        </div>

        <div style={{ marginTop: '20px', fontSize: '14px', color: '#666' }}>
          <strong>Base value:</strong> {base_value.toFixed(4)}
        </div>
      </div>
    );
  }

  return (
    <div className="container">
      <h1>Bank Customer Risk Assessment</h1>

      <div className="search-box">
        <form onSubmit={handleSearch}>
          <input
            type="text"
            placeholder="Enter Customer ID"
            value={customerId}
            onChange={(e) => setCustomerId(e.target.value)}
          />
          <button type="submit" disabled={loading}>
            {loading ? 'Searching...' : 'Search'}
          </button>
        </form>
      </div>

      {error && <p className="error">{error}</p>}

      {customerData && (
        <div className="content">
          <div className="customer-details-card">
            <h2>Customer Profile</h2>
            <div className="detail-row">
              <strong>ID:</strong> <span>{customerData.customer.id}</span>
            </div>
            <div className="detail-row">
              <strong>Age:</strong> <span>{customerData.customer.age}</span>
            </div>
            <div className="detail-row">
              <strong>Monthly Income:</strong> <span>{customerData.customer.MonthlyIncome}</span>
            </div>
            <div className="detail-row">
              <strong>Debt Ratio:</strong> <span>{customerData.customer.DebtRatio}</span>
            </div>
            <div className="detail-row">
              <strong>Dependents:</strong> <span>{customerData.customer.NumberOfDependents}</span>
            </div>
          </div>

          <div className="risk-score-card">
            <h2>Risk Assessment</h2>
            <div className={`score-display ${typeof customerData.riskScore === 'number' && customerData.riskScore > 0.5 ? 'high-risk' : 'low-risk'}`}>
              {customerData.riskScore}
            </div>
            <p>Score indicates probability of default.</p>
          </div>
        </div>
      )}

      {loadingExplanation && <p>Loading explanation...</p>}

      {explanation && renderExplanation()}
    </div>
  )
}

export default App
