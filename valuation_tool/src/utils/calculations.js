/**
 * Business Valuation Calculation Engine
 *
 * Implements three core valuation methodologies:
 * 1. Revenue Multiple Method
 * 2. EBITDA Multiple Method
 * 3. Asset-Based Method
 */

import { getIndustryById, getAdjustedMultiplier } from './industryData';

/**
 * Format number as currency (USD)
 * @param {number} value - Numeric value to format
 * @returns {string} Formatted currency string
 */
export const formatCurrency = (value) => {
  if (!value && value !== 0) return '$0';

  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0
  }).format(value);
};

/**
 * Round to nearest thousand
 * @param {number} value - Value to round
 * @returns {number} Rounded value
 */
export const roundToThousand = (value) => {
  return Math.round(value / 1000) * 1000;
};

/**
 * Calculate confidence level based on data quality
 * @param {object} businessData - Business financial data
 * @param {string} method - Valuation method used
 * @returns {string} Confidence level: 'low', 'medium', or 'high'
 */
export const calculateConfidence = (businessData, method) => {
  let score = 0;

  // Check data completeness
  if (businessData.annualRevenue > 0) score += 1;
  if (businessData.annualProfit) score += 1;
  if (businessData.ebitda) score += 1;
  if (businessData.totalAssets > 0) score += 1;
  if (businessData.yearsFounded > 0) score += 1;

  // Method-specific confidence
  if (method === 'revenue' && businessData.annualRevenue > 0) score += 1;
  if (method === 'ebitda' && businessData.ebitda > 0) score += 2;
  if (method === 'asset' && businessData.totalAssets > 0 && businessData.totalLiabilities >= 0) score += 2;

  // Determine confidence level
  if (score >= 7) return 'high';
  if (score >= 4) return 'medium';
  return 'low';
};

/**
 * Revenue Multiple Valuation Method
 * Formula: Business Value = Annual Revenue × Industry Multiplier
 *
 * @param {object} businessData - Business financial data
 * @returns {object} Valuation result
 */
export const calculateRevenueMultiple = (businessData) => {
  const { annualRevenue, industry } = businessData;

  // Validation
  if (!annualRevenue || annualRevenue <= 0) {
    return {
      error: 'Annual revenue is required for this method',
      estimatedValue: 0
    };
  }

  if (!industry) {
    return {
      error: 'Please select an industry',
      estimatedValue: 0
    };
  }

  // Get industry data and multiplier
  const industryData = getIndustryById(industry);
  if (!industryData) {
    return {
      error: 'Invalid industry selected',
      estimatedValue: 0
    };
  }

  const multiplier = getAdjustedMultiplier(industryData, 'revenue', businessData);
  const rawValue = annualRevenue * multiplier;
  const estimatedValue = roundToThousand(rawValue);

  // Build explanation
  const assumptions = [
    `Industry: ${industryData.name}`,
    `Base multiplier range: ${industryData.revenueMultiplier.low}x - ${industryData.revenueMultiplier.high}x`,
    `Adjusted multiplier: ${multiplier.toFixed(2)}x`,
  ];

  if (businessData.revenueGrowthRate) {
    assumptions.push(`Growth rate: ${businessData.revenueGrowthRate}%`);
  }

  if (businessData.yearsFounded) {
    assumptions.push(`Years in business: ${businessData.yearsFounded}`);
  }

  return {
    method: 'Revenue Multiple',
    methodId: 'revenue',
    estimatedValue,
    multiplier: multiplier.toFixed(2),
    confidence: calculateConfidence(businessData, 'revenue'),
    breakdown: {
      description: 'Values businesses based on annual revenue multiplied by industry-specific factors.',
      calculation: `${formatCurrency(annualRevenue)} × ${multiplier.toFixed(2)} = ${formatCurrency(estimatedValue)}`,
      assumptions,
      whenToUse: 'Best for businesses with consistent revenue, especially in industries where revenue multiples are standard (SaaS, e-commerce).'
    }
  };
};

/**
 * EBITDA Multiple Valuation Method
 * Formula: Business Value = EBITDA × Industry Multiplier
 *
 * @param {object} businessData - Business financial data
 * @returns {object} Valuation result
 */
export const calculateEBITDAMultiple = (businessData) => {
  const { ebitda, industry, annualRevenue } = businessData;

  // Validation
  if (!ebitda && ebitda !== 0) {
    return {
      error: 'EBITDA is required for this method',
      estimatedValue: 0
    };
  }

  if (ebitda <= 0) {
    return {
      error: 'EBITDA must be positive for this method. Consider using Revenue Multiple or Asset-Based methods instead.',
      estimatedValue: 0
    };
  }

  if (!industry) {
    return {
      error: 'Please select an industry',
      estimatedValue: 0
    };
  }

  // Get industry data and multiplier
  const industryData = getIndustryById(industry);
  if (!industryData) {
    return {
      error: 'Invalid industry selected',
      estimatedValue: 0
    };
  }

  const multiplier = getAdjustedMultiplier(industryData, 'ebitda', businessData);
  const rawValue = ebitda * multiplier;
  const estimatedValue = roundToThousand(rawValue);

  // Calculate EBITDA margin for additional insight
  const ebitdaMargin = annualRevenue > 0 ? ((ebitda / annualRevenue) * 100).toFixed(1) : 'N/A';

  // Build explanation
  const assumptions = [
    `Industry: ${industryData.name}`,
    `Base multiplier range: ${industryData.ebitdaMultiplier.low}x - ${industryData.ebitdaMultiplier.high}x`,
    `Adjusted multiplier: ${multiplier.toFixed(2)}x`,
    `EBITDA margin: ${ebitdaMargin}%`
  ];

  if (businessData.revenueGrowthRate) {
    assumptions.push(`Growth rate: ${businessData.revenueGrowthRate}%`);
  }

  if (businessData.yearsFounded) {
    assumptions.push(`Years in business: ${businessData.yearsFounded}`);
  }

  return {
    method: 'EBITDA Multiple',
    methodId: 'ebitda',
    estimatedValue,
    multiplier: multiplier.toFixed(2),
    confidence: calculateConfidence(businessData, 'ebitda'),
    breakdown: {
      description: 'Values businesses based on earnings before interest, taxes, depreciation, and amortization.',
      calculation: `${formatCurrency(ebitda)} × ${multiplier.toFixed(2)} = ${formatCurrency(estimatedValue)}`,
      assumptions,
      whenToUse: 'Preferred method for profitable businesses with good margins. Most accurate for mature, stable businesses.'
    }
  };
};

/**
 * Asset-Based Valuation Method
 * Formula: Business Value = (Total Assets - Total Liabilities) × Multiplier
 *
 * @param {object} businessData - Business financial data
 * @returns {object} Valuation result
 */
export const calculateAssetBased = (businessData) => {
  const { totalAssets, totalLiabilities, industry } = businessData;

  // Validation
  if (!totalAssets && totalAssets !== 0) {
    return {
      error: 'Total assets is required for this method',
      estimatedValue: 0
    };
  }

  if (totalAssets <= 0) {
    return {
      error: 'Total assets must be positive',
      estimatedValue: 0
    };
  }

  const liabilities = totalLiabilities || 0;

  if (liabilities < 0) {
    return {
      error: 'Total liabilities cannot be negative',
      estimatedValue: 0
    };
  }

  // Calculate book value (net assets)
  const bookValue = totalAssets - liabilities;

  if (bookValue <= 0) {
    return {
      error: 'Net assets (Assets - Liabilities) must be positive for this method',
      estimatedValue: 0
    };
  }

  // Get industry data for context
  const industryData = industry ? getIndustryById(industry) : null;

  // Asset-based multiplier (typically 0.7 - 1.3 of book value)
  // Adjusted based on industry and business characteristics
  let multiplier = 1.0; // Start at book value

  if (industryData) {
    // Asset-heavy industries might command premium
    if (['manufacturing', 'retail', 'real_estate'].includes(industryData.id)) {
      multiplier = 1.1;
    }
    // Service businesses typically discount from book
    if (['professional_services', 'saas'].includes(industryData.id)) {
      multiplier = 0.85;
    }
  }

  // Adjust for profitability if available
  if (businessData.annualProfit) {
    if (businessData.annualProfit > 0) {
      multiplier += 0.1; // Profitable: small premium
    } else {
      multiplier -= 0.15; // Unprofitable: discount
    }
  }

  // Ensure multiplier stays in reasonable range
  multiplier = Math.max(0.7, Math.min(1.3, multiplier));

  const rawValue = bookValue * multiplier;
  const estimatedValue = roundToThousand(rawValue);

  // Build explanation
  const assumptions = [
    `Total assets: ${formatCurrency(totalAssets)}`,
    `Total liabilities: ${formatCurrency(liabilities)}`,
    `Net assets (book value): ${formatCurrency(bookValue)}`,
    `Valuation multiplier: ${multiplier.toFixed(2)}x book value`
  ];

  if (industryData) {
    assumptions.push(`Industry: ${industryData.name}`);
  }

  return {
    method: 'Asset-Based',
    methodId: 'asset',
    estimatedValue,
    multiplier: multiplier.toFixed(2),
    confidence: calculateConfidence(businessData, 'asset'),
    breakdown: {
      description: 'Values businesses based on net assets (total assets minus liabilities).',
      calculation: `(${formatCurrency(totalAssets)} - ${formatCurrency(liabilities)}) × ${multiplier.toFixed(2)} = ${formatCurrency(estimatedValue)}`,
      assumptions,
      whenToUse: 'Best for asset-heavy businesses or when earnings-based methods are not applicable (e.g., negative earnings).'
    }
  };
};

/**
 * Calculate valuation using all available methods
 * @param {object} businessData - Business financial data
 * @returns {array} Array of valuation results
 */
export const calculateAllMethods = (businessData) => {
  const results = [];

  // Try revenue multiple
  const revenueResult = calculateRevenueMultiple(businessData);
  if (!revenueResult.error) {
    results.push(revenueResult);
  }

  // Try EBITDA multiple
  const ebitdaResult = calculateEBITDAMultiple(businessData);
  if (!ebitdaResult.error) {
    results.push(ebitdaResult);
  }

  // Try asset-based
  const assetResult = calculateAssetBased(businessData);
  if (!assetResult.error) {
    results.push(assetResult);
  }

  return results;
};

/**
 * Get the recommended valuation method based on business data
 * @param {object} businessData - Business financial data
 * @returns {string} Recommended method: 'revenue', 'ebitda', or 'asset'
 */
export const getRecommendedMethod = (businessData) => {
  const { ebitda, annualRevenue, annualProfit, totalAssets } = businessData;

  // Prefer EBITDA if available and positive with good margin
  if (ebitda && ebitda > 0 && annualRevenue > 0) {
    const margin = (ebitda / annualRevenue) * 100;
    if (margin > 10) {
      return 'ebitda';
    }
  }

  // Use revenue multiple if revenue is available
  if (annualRevenue && annualRevenue > 0) {
    return 'revenue';
  }

  // Fall back to asset-based
  if (totalAssets && totalAssets > 0) {
    return 'asset';
  }

  // Default to revenue
  return 'revenue';
};
