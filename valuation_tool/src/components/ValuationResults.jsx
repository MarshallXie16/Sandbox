import { formatCurrency } from '../utils/calculations';
import { calculateRevenueMultiple, calculateEBITDAMultiple, calculateAssetBased } from '../utils/calculations';
import './ValuationResults.css';

/**
 * ValuationResults Component
 * Displays valuation calculation results with explanations
 */
const ValuationResults = ({ result, businessData, onEdit, onReset }) => {
  // Calculate all methods for comparison
  const allResults = [];

  const revenueResult = calculateRevenueMultiple(businessData);
  if (!revenueResult.error) allResults.push(revenueResult);

  const ebitdaResult = calculateEBITDAMultiple(businessData);
  if (!ebitdaResult.error) allResults.push(ebitdaResult);

  const assetResult = calculateAssetBased(businessData);
  if (!assetResult.error) allResults.push(assetResult);

  /**
   * Get confidence badge color
   */
  const getConfidenceBadgeClass = (confidence) => {
    switch (confidence) {
      case 'high':
        return 'confidence-high';
      case 'medium':
        return 'confidence-medium';
      case 'low':
        return 'confidence-low';
      default:
        return 'confidence-medium';
    }
  };

  /**
   * Get confidence description
   */
  const getConfidenceDescription = (confidence) => {
    switch (confidence) {
      case 'high':
        return 'This valuation is based on complete data and is relatively reliable.';
      case 'medium':
        return 'This valuation is based on partial data. Consider adding more financial details for a better estimate.';
      case 'low':
        return 'This valuation is based on limited data. Adding more financial information will significantly improve accuracy.';
      default:
        return '';
    }
  };

  // Handle error case
  if (result.error) {
    return (
      <div className="valuation-results-container">
        <div className="error-result">
          <h2>Unable to Calculate</h2>
          <p className="error-message">{result.error}</p>
          <div className="action-buttons">
            <button onClick={onEdit} className="btn-secondary">
              Edit Information
            </button>
            <button onClick={onReset} className="btn-outline">
              Start Over
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="valuation-results-container">
      <div className="results-header">
        <h1>Business Valuation Estimate</h1>
        <p className="business-name">{businessData.businessName}</p>
      </div>

      <div className="main-result">
        <div className="result-card primary">
          <span className="result-label">{result.method} Valuation</span>
          <div className="result-value">{formatCurrency(result.estimatedValue)}</div>
          <div className={`confidence-badge ${getConfidenceBadgeClass(result.confidence)}`}>
            {result.confidence.toUpperCase()} CONFIDENCE
          </div>
          <p className="confidence-description">
            {getConfidenceDescription(result.confidence)}
          </p>
        </div>
      </div>

      <div className="calculation-breakdown">
        <h2>How We Calculated This</h2>
        <div className="breakdown-content">
          <div className="breakdown-section">
            <h3>Method</h3>
            <p>{result.breakdown.description}</p>
          </div>

          <div className="breakdown-section">
            <h3>Calculation</h3>
            <p className="calculation-formula">{result.breakdown.calculation}</p>
          </div>

          <div className="breakdown-section">
            <h3>Assumptions</h3>
            <ul className="assumptions-list">
              {result.breakdown.assumptions.map((assumption, index) => (
                <li key={index}>{assumption}</li>
              ))}
            </ul>
          </div>

          <div className="breakdown-section">
            <h3>When to Use This Method</h3>
            <p>{result.breakdown.whenToUse}</p>
          </div>
        </div>
      </div>

      {allResults.length > 1 && (
        <div className="comparison-section">
          <h2>Compare All Methods</h2>
          <p className="comparison-intro">
            Here are valuations using all applicable methods. Different methods may yield different results based on your business characteristics.
          </p>
          <div className="comparison-grid">
            {allResults.map((methodResult, index) => (
              <div
                key={index}
                className={`comparison-card ${methodResult.methodId === result.methodId ? 'active' : ''}`}
              >
                <h3>{methodResult.method}</h3>
                <div className="comparison-value">{formatCurrency(methodResult.estimatedValue)}</div>
                <div className={`confidence-badge small ${getConfidenceBadgeClass(methodResult.confidence)}`}>
                  {methodResult.confidence}
                </div>
                <p className="comparison-desc">{methodResult.breakdown.description}</p>
              </div>
            ))}
          </div>

          {allResults.length > 1 && (
            <div className="valuation-range">
              <h3>Valuation Range</h3>
              <p>
                Based on all methods:{' '}
                <strong>
                  {formatCurrency(Math.min(...allResults.map(r => r.estimatedValue)))}
                </strong>
                {' to '}
                <strong>
                  {formatCurrency(Math.max(...allResults.map(r => r.estimatedValue)))}
                </strong>
              </p>
              <p className="range-note">
                This range reflects different valuation perspectives. The most appropriate method depends on your industry, business model, and financial performance.
              </p>
            </div>
          )}
        </div>
      )}

      <div className="next-steps">
        <h2>Next Steps</h2>
        <div className="next-steps-content">
          <div className="step-card">
            <h3>1. Review the Results</h3>
            <p>This is a preliminary estimate. Actual valuations may vary based on market conditions, growth potential, and other qualitative factors.</p>
          </div>
          <div className="step-card">
            <h3>2. Improve Accuracy</h3>
            <p>For a more accurate estimate, ensure all financial fields are filled in. Consider using multiple valuation methods for comparison.</p>
          </div>
          <div className="step-card">
            <h3>3. Consult a Professional</h3>
            <p>For transactions, legal matters, or tax purposes, consult a certified business appraiser or valuation professional.</p>
          </div>
        </div>
      </div>

      <div className="action-buttons">
        <button onClick={onEdit} className="btn-primary">
          Refine Inputs
        </button>
        <button onClick={onReset} className="btn-secondary">
          Start New Valuation
        </button>
      </div>

      <div className="disclaimer-box">
        <h3>Important Disclaimer</h3>
        <p>
          This calculator provides educational estimates only and should not be used as the sole basis for any financial, legal, or business decisions. Business valuations are complex and require consideration of many factors not captured in this simple calculator, including market conditions, competitive positioning, growth potential, customer concentration, intellectual property, and many other qualitative and quantitative factors.
        </p>
        <p>
          For any significant business transaction, legal matter, tax purpose, or financial decision, please consult with a qualified business valuation professional, certified public accountant, or financial advisor.
        </p>
      </div>
    </div>
  );
};

export default ValuationResults;
