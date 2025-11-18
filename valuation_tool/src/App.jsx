import { useState } from 'react';
import './App.css';
import ValuationForm from './components/ValuationForm';
import ValuationResults from './components/ValuationResults';
import { calculateRevenueMultiple, calculateEBITDAMultiple, calculateAssetBased, getRecommendedMethod } from './utils/calculations';

function App() {
  const [businessData, setBusinessData] = useState({
    businessName: '',
    industry: '',
    annualRevenue: '',
    annualProfit: '',
    ebitda: '',
    totalAssets: '',
    totalLiabilities: '',
    revenueGrowthRate: '',
    yearsFounded: ''
  });

  const [selectedMethod, setSelectedMethod] = useState('revenue');
  const [valuationResult, setValuationResult] = useState(null);
  const [showResults, setShowResults] = useState(false);

  /**
   * Handle form submission
   * @param {object} data - Business data from form
   */
  const handleCalculate = (data) => {
    setBusinessData(data);

    // Calculate valuation based on selected method
    let result;

    switch (selectedMethod) {
      case 'revenue':
        result = calculateRevenueMultiple(data);
        break;
      case 'ebitda':
        result = calculateEBITDAMultiple(data);
        break;
      case 'asset':
        result = calculateAssetBased(data);
        break;
      default:
        result = calculateRevenueMultiple(data);
    }

    setValuationResult(result);
    setShowResults(true);
  };

  /**
   * Reset the form and results
   */
  const handleReset = () => {
    setBusinessData({
      businessName: '',
      industry: '',
      annualRevenue: '',
      annualProfit: '',
      ebitda: '',
      totalAssets: '',
      totalLiabilities: '',
      revenueGrowthRate: '',
      yearsFounded: ''
    });
    setValuationResult(null);
    setShowResults(false);
  };

  /**
   * Go back to edit form
   */
  const handleEdit = () => {
    setShowResults(false);
  };

  return (
    <div className="app">
      <header className="app-header">
        <h1>Business Valuation Calculator</h1>
        <p className="tagline">Get a quick estimate of your business value</p>
      </header>

      <main className="app-main">
        {!showResults ? (
          <ValuationForm
            initialData={businessData}
            selectedMethod={selectedMethod}
            onMethodChange={setSelectedMethod}
            onCalculate={handleCalculate}
          />
        ) : (
          <ValuationResults
            result={valuationResult}
            businessData={businessData}
            onEdit={handleEdit}
            onReset={handleReset}
          />
        )}
      </main>

      <footer className="app-footer">
        <p className="disclaimer">
          <strong>Disclaimer:</strong> This tool provides preliminary estimates only.
          For legal, tax, or transaction purposes, please consult a certified business
          valuator or financial professional.
        </p>
        <p className="copyright">
          © 2024 Business Valuation Calculator | Educational purposes only
        </p>
      </footer>
    </div>
  );
}

export default App;
