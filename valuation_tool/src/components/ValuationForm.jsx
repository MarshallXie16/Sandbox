import { useState, useEffect } from 'react';
import { getIndustryOptions } from '../utils/industryData';
import { validateBusinessData, parseCurrency, formatNumberInput } from '../utils/validators';
import './ValuationForm.css';

/**
 * ValuationForm Component
 * Collects business financial data and calculates valuation
 */
const ValuationForm = ({ initialData, selectedMethod, onMethodChange, onCalculate }) => {
  const [formData, setFormData] = useState(initialData);
  const [errors, setErrors] = useState({});
  const [touched, setTouched] = useState({});

  const industries = getIndustryOptions();

  useEffect(() => {
    setFormData(initialData);
  }, [initialData]);

  /**
   * Handle input change
   */
  const handleChange = (e) => {
    const { name, value } = e.target;

    // For numeric fields, clean the input
    if (['annualRevenue', 'annualProfit', 'ebitda', 'totalAssets', 'totalLiabilities', 'revenueGrowthRate', 'yearsFounded'].includes(name)) {
      const cleaned = formatNumberInput(value);
      setFormData(prev => ({
        ...prev,
        [name]: cleaned
      }));
    } else {
      setFormData(prev => ({
        ...prev,
        [name]: value
      }));
    }

    // Clear error for this field when user types
    if (errors[name]) {
      setErrors(prev => ({
        ...prev,
        [name]: null
      }));
    }
  };

  /**
   * Handle input blur (for validation)
   */
  const handleBlur = (e) => {
    const { name } = e.target;
    setTouched(prev => ({
      ...prev,
      [name]: true
    }));
  };

  /**
   * Handle form submission
   */
  const handleSubmit = (e) => {
    e.preventDefault();

    // Convert string inputs to numbers
    const dataToValidate = {
      ...formData,
      annualRevenue: parseCurrency(formData.annualRevenue),
      annualProfit: parseCurrency(formData.annualProfit) || null,
      ebitda: parseCurrency(formData.ebitda) || null,
      totalAssets: parseCurrency(formData.totalAssets) || null,
      totalLiabilities: parseCurrency(formData.totalLiabilities) || null,
      revenueGrowthRate: parseFloat(formData.revenueGrowthRate) || null,
      yearsFounded: parseInt(formData.yearsFounded) || null
    };

    // Validate
    const validation = validateBusinessData(dataToValidate);

    if (!validation.isValid) {
      setErrors(validation.errors);
      // Mark all fields as touched to show errors
      const allTouched = {};
      Object.keys(formData).forEach(key => {
        allTouched[key] = true;
      });
      setTouched(allTouched);
      return;
    }

    // Clear errors and submit
    setErrors({});
    onCalculate(dataToValidate);
  };

  /**
   * Get field-specific requirements based on selected method
   */
  const getFieldRequirement = (fieldName) => {
    if (selectedMethod === 'revenue' && fieldName === 'annualRevenue') return 'required';
    if (selectedMethod === 'ebitda' && fieldName === 'ebitda') return 'required';
    if (selectedMethod === 'asset' && (fieldName === 'totalAssets')) return 'required';
    return 'optional';
  };

  return (
    <div className="valuation-form-container">
      <div className="method-selector">
        <h2>Select Valuation Method</h2>
        <div className="method-buttons">
          <button
            type="button"
            className={`method-btn ${selectedMethod === 'revenue' ? 'active' : ''}`}
            onClick={() => onMethodChange('revenue')}
          >
            <span className="method-name">Revenue Multiple</span>
            <span className="method-desc">Based on annual sales</span>
          </button>
          <button
            type="button"
            className={`method-btn ${selectedMethod === 'ebitda' ? 'active' : ''}`}
            onClick={() => onMethodChange('ebitda')}
          >
            <span className="method-name">EBITDA Multiple</span>
            <span className="method-desc">Based on earnings</span>
          </button>
          <button
            type="button"
            className={`method-btn ${selectedMethod === 'asset' ? 'active' : ''}`}
            onClick={() => onMethodChange('asset')}
          >
            <span className="method-name">Asset-Based</span>
            <span className="method-desc">Based on net assets</span>
          </button>
        </div>
      </div>

      <form onSubmit={handleSubmit} className="valuation-form" noValidate>
        <h2>Business Information</h2>

        <div className="form-section">
          <div className="form-group">
            <label htmlFor="businessName">
              Business Name <span className="required">*</span>
            </label>
            <input
              type="text"
              id="businessName"
              name="businessName"
              value={formData.businessName}
              onChange={handleChange}
              onBlur={handleBlur}
              placeholder="e.g., Acme Corporation"
              className={errors.businessName && touched.businessName ? 'error' : ''}
            />
            {errors.businessName && touched.businessName && (
              <span className="error-message">{errors.businessName}</span>
            )}
          </div>

          <div className="form-group">
            <label htmlFor="industry">
              Industry <span className="required">*</span>
            </label>
            <select
              id="industry"
              name="industry"
              value={formData.industry}
              onChange={handleChange}
              onBlur={handleBlur}
              className={errors.industry && touched.industry ? 'error' : ''}
            >
              <option value="">-- Select Industry --</option>
              {industries.map(ind => (
                <option key={ind.id} value={ind.id}>
                  {ind.name}
                </option>
              ))}
            </select>
            {errors.industry && touched.industry && (
              <span className="error-message">{errors.industry}</span>
            )}
          </div>
        </div>

        <h2>Financial Metrics</h2>

        <div className="form-section">
          <div className="form-group">
            <label htmlFor="annualRevenue">
              Annual Revenue <span className="required">*</span>
              <span className="help-text">Total sales for the past 12 months</span>
            </label>
            <div className="input-wrapper">
              <span className="currency-symbol">$</span>
              <input
                type="text"
                id="annualRevenue"
                name="annualRevenue"
                value={formData.annualRevenue}
                onChange={handleChange}
                onBlur={handleBlur}
                placeholder="500000"
                className={errors.annualRevenue && touched.annualRevenue ? 'error with-symbol' : 'with-symbol'}
              />
            </div>
            {errors.annualRevenue && touched.annualRevenue && (
              <span className="error-message">{errors.annualRevenue}</span>
            )}
          </div>

          <div className="form-group">
            <label htmlFor="annualProfit">
              Annual Net Profit
              {selectedMethod === 'ebitda' && <span className="optional"> (optional)</span>}
              <span className="help-text">Net profit after all expenses</span>
            </label>
            <div className="input-wrapper">
              <span className="currency-symbol">$</span>
              <input
                type="text"
                id="annualProfit"
                name="annualProfit"
                value={formData.annualProfit}
                onChange={handleChange}
                onBlur={handleBlur}
                placeholder="75000"
                className={errors.annualProfit && touched.annualProfit ? 'error with-symbol' : 'with-symbol'}
              />
            </div>
            {errors.annualProfit && touched.annualProfit && (
              <span className="error-message">{errors.annualProfit}</span>
            )}
          </div>
        </div>

        <div className="form-section">
          <div className="form-group">
            <label htmlFor="ebitda">
              EBITDA {selectedMethod === 'ebitda' ? <span className="required">*</span> : <span className="optional">(optional)</span>}
              <span className="help-text">Earnings before interest, taxes, depreciation, amortization</span>
            </label>
            <div className="input-wrapper">
              <span className="currency-symbol">$</span>
              <input
                type="text"
                id="ebitda"
                name="ebitda"
                value={formData.ebitda}
                onChange={handleChange}
                onBlur={handleBlur}
                placeholder="100000"
                className={errors.ebitda && touched.ebitda ? 'error with-symbol' : 'with-symbol'}
              />
            </div>
            {errors.ebitda && touched.ebitda && (
              <span className="error-message">{errors.ebitda}</span>
            )}
          </div>

          <div className="form-group">
            <label htmlFor="totalAssets">
              Total Assets {selectedMethod === 'asset' ? <span className="required">*</span> : <span className="optional">(optional)</span>}
              <span className="help-text">Total value of everything your business owns</span>
            </label>
            <div className="input-wrapper">
              <span className="currency-symbol">$</span>
              <input
                type="text"
                id="totalAssets"
                name="totalAssets"
                value={formData.totalAssets}
                onChange={handleChange}
                onBlur={handleBlur}
                placeholder="250000"
                className={errors.totalAssets && touched.totalAssets ? 'error with-symbol' : 'with-symbol'}
              />
            </div>
            {errors.totalAssets && touched.totalAssets && (
              <span className="error-message">{errors.totalAssets}</span>
            )}
          </div>
        </div>

        <div className="form-section">
          <div className="form-group">
            <label htmlFor="totalLiabilities">
              Total Liabilities <span className="optional">(optional)</span>
              <span className="help-text">Total debts and obligations</span>
            </label>
            <div className="input-wrapper">
              <span className="currency-symbol">$</span>
              <input
                type="text"
                id="totalLiabilities"
                name="totalLiabilities"
                value={formData.totalLiabilities}
                onChange={handleChange}
                onBlur={handleBlur}
                placeholder="100000"
                className={errors.totalLiabilities && touched.totalLiabilities ? 'error with-symbol' : 'with-symbol'}
              />
            </div>
            {errors.totalLiabilities && touched.totalLiabilities && (
              <span className="error-message">{errors.totalLiabilities}</span>
            )}
          </div>

          <div className="form-group">
            <label htmlFor="revenueGrowthRate">
              Revenue Growth Rate <span className="optional">(optional)</span>
              <span className="help-text">Year-over-year percentage change</span>
            </label>
            <div className="input-wrapper">
              <input
                type="text"
                id="revenueGrowthRate"
                name="revenueGrowthRate"
                value={formData.revenueGrowthRate}
                onChange={handleChange}
                onBlur={handleBlur}
                placeholder="15"
                className={errors.revenueGrowthRate && touched.revenueGrowthRate ? 'error with-symbol' : 'with-symbol'}
              />
              <span className="unit-symbol">%</span>
            </div>
            {errors.revenueGrowthRate && touched.revenueGrowthRate && (
              <span className="error-message">{errors.revenueGrowthRate}</span>
            )}
          </div>
        </div>

        <div className="form-section">
          <div className="form-group">
            <label htmlFor="yearsFounded">
              Years in Business <span className="optional">(optional)</span>
              <span className="help-text">How long has the business been operating?</span>
            </label>
            <input
              type="text"
              id="yearsFounded"
              name="yearsFounded"
              value={formData.yearsFounded}
              onChange={handleChange}
              onBlur={handleBlur}
              placeholder="5"
              className={errors.yearsFounded && touched.yearsFounded ? 'error' : ''}
            />
            {errors.yearsFounded && touched.yearsFounded && (
              <span className="error-message">{errors.yearsFounded}</span>
            )}
          </div>
        </div>

        <button type="submit" className="calculate-btn">
          Calculate Business Value
        </button>
      </form>
    </div>
  );
};

export default ValuationForm;
