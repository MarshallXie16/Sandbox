/**
 * Input Validation Utilities
 *
 * Validates user inputs for business valuation calculations
 */

/**
 * Validate numeric input
 * @param {string|number} value - Value to validate
 * @param {object} options - Validation options
 * @returns {object} {isValid: boolean, error: string}
 */
export const validateNumber = (value, options = {}) => {
  const {
    min = null,
    max = null,
    required = false,
    allowNegative = false,
    fieldName = 'This field'
  } = options;

  // Check if required
  if (required && (value === null || value === undefined || value === '')) {
    return {
      isValid: false,
      error: `${fieldName} is required`
    };
  }

  // Allow empty for optional fields
  if (!required && (value === null || value === undefined || value === '')) {
    return {
      isValid: true,
      error: null
    };
  }

  // Convert to number
  const numValue = typeof value === 'string' ? parseFloat(value.replace(/[,$]/g, '')) : value;

  // Check if valid number
  if (isNaN(numValue)) {
    return {
      isValid: false,
      error: `${fieldName} must be a valid number`
    };
  }

  // Check negative
  if (!allowNegative && numValue < 0) {
    return {
      isValid: false,
      error: `${fieldName} cannot be negative`
    };
  }

  // Check min
  if (min !== null && numValue < min) {
    return {
      isValid: false,
      error: `${fieldName} must be at least ${min}`
    };
  }

  // Check max
  if (max !== null && numValue > max) {
    return {
      isValid: false,
      error: `${fieldName} must be at most ${max.toLocaleString()}`
    };
  }

  return {
    isValid: true,
    error: null
  };
};

/**
 * Validate annual revenue
 * @param {number} value - Revenue value
 * @returns {object} Validation result
 */
export const validateRevenue = (value) => {
  return validateNumber(value, {
    min: 1,
    max: 10000000000, // 10 billion
    required: true,
    allowNegative: false,
    fieldName: 'Annual revenue'
  });
};

/**
 * Validate profit (can be negative)
 * @param {number} value - Profit value
 * @returns {object} Validation result
 */
export const validateProfit = (value) => {
  return validateNumber(value, {
    min: -100000000, // -100 million
    max: 10000000000, // 10 billion
    required: false,
    allowNegative: true,
    fieldName: 'Annual profit'
  });
};

/**
 * Validate EBITDA (can be negative)
 * @param {number} value - EBITDA value
 * @returns {object} Validation result
 */
export const validateEBITDA = (value) => {
  return validateNumber(value, {
    min: -100000000,
    max: 10000000000,
    required: false,
    allowNegative: true,
    fieldName: 'EBITDA'
  });
};

/**
 * Validate assets
 * @param {number} value - Assets value
 * @returns {object} Validation result
 */
export const validateAssets = (value) => {
  return validateNumber(value, {
    min: 0,
    max: 100000000000, // 100 billion
    required: false,
    allowNegative: false,
    fieldName: 'Total assets'
  });
};

/**
 * Validate liabilities
 * @param {number} value - Liabilities value
 * @returns {object} Validation result
 */
export const validateLiabilities = (value) => {
  return validateNumber(value, {
    min: 0,
    max: 100000000000,
    required: false,
    allowNegative: false,
    fieldName: 'Total liabilities'
  });
};

/**
 * Validate growth rate (percentage)
 * @param {number} value - Growth rate
 * @returns {object} Validation result
 */
export const validateGrowthRate = (value) => {
  return validateNumber(value, {
    min: -100,
    max: 1000,
    required: false,
    allowNegative: true,
    fieldName: 'Revenue growth rate'
  });
};

/**
 * Validate years founded
 * @param {number} value - Years in business
 * @returns {object} Validation result
 */
export const validateYearsFounded = (value) => {
  return validateNumber(value, {
    min: 0,
    max: 200,
    required: false,
    allowNegative: false,
    fieldName: 'Years in business'
  });
};

/**
 * Validate industry selection
 * @param {string} value - Industry ID
 * @returns {object} Validation result
 */
export const validateIndustry = (value) => {
  if (!value || value === '') {
    return {
      isValid: false,
      error: 'Please select an industry'
    };
  }

  return {
    isValid: true,
    error: null
  };
};

/**
 * Validate business name
 * @param {string} value - Business name
 * @returns {object} Validation result
 */
export const validateBusinessName = (value) => {
  if (!value || value.trim() === '') {
    return {
      isValid: false,
      error: 'Business name is required'
    };
  }

  if (value.length > 100) {
    return {
      isValid: false,
      error: 'Business name must be less than 100 characters'
    };
  }

  return {
    isValid: true,
    error: null
  };
};

/**
 * Validate entire business data object
 * @param {object} businessData - Complete business data
 * @returns {object} {isValid: boolean, errors: object}
 */
export const validateBusinessData = (businessData) => {
  const errors = {};

  // Validate business name
  const nameValidation = validateBusinessName(businessData.businessName);
  if (!nameValidation.isValid) {
    errors.businessName = nameValidation.error;
  }

  // Validate industry
  const industryValidation = validateIndustry(businessData.industry);
  if (!industryValidation.isValid) {
    errors.industry = industryValidation.error;
  }

  // Validate revenue
  const revenueValidation = validateRevenue(businessData.annualRevenue);
  if (!revenueValidation.isValid) {
    errors.annualRevenue = revenueValidation.error;
  }

  // Validate profit (optional)
  if (businessData.annualProfit !== null && businessData.annualProfit !== undefined && businessData.annualProfit !== '') {
    const profitValidation = validateProfit(businessData.annualProfit);
    if (!profitValidation.isValid) {
      errors.annualProfit = profitValidation.error;
    }
  }

  // Validate EBITDA (optional)
  if (businessData.ebitda !== null && businessData.ebitda !== undefined && businessData.ebitda !== '') {
    const ebitdaValidation = validateEBITDA(businessData.ebitda);
    if (!ebitdaValidation.isValid) {
      errors.ebitda = ebitdaValidation.error;
    }
  }

  // Validate assets (optional)
  if (businessData.totalAssets !== null && businessData.totalAssets !== undefined && businessData.totalAssets !== '') {
    const assetsValidation = validateAssets(businessData.totalAssets);
    if (!assetsValidation.isValid) {
      errors.totalAssets = assetsValidation.error;
    }
  }

  // Validate liabilities (optional)
  if (businessData.totalLiabilities !== null && businessData.totalLiabilities !== undefined && businessData.totalLiabilities !== '') {
    const liabilitiesValidation = validateLiabilities(businessData.totalLiabilities);
    if (!liabilitiesValidation.isValid) {
      errors.totalLiabilities = liabilitiesValidation.error;
    }
  }

  // Validate growth rate (optional)
  if (businessData.revenueGrowthRate !== null && businessData.revenueGrowthRate !== undefined && businessData.revenueGrowthRate !== '') {
    const growthValidation = validateGrowthRate(businessData.revenueGrowthRate);
    if (!growthValidation.isValid) {
      errors.revenueGrowthRate = growthValidation.error;
    }
  }

  // Validate years founded (optional)
  if (businessData.yearsFounded !== null && businessData.yearsFounded !== undefined && businessData.yearsFounded !== '') {
    const yearsValidation = validateYearsFounded(businessData.yearsFounded);
    if (!yearsValidation.isValid) {
      errors.yearsFounded = yearsValidation.error;
    }
  }

  return {
    isValid: Object.keys(errors).length === 0,
    errors
  };
};

/**
 * Format number input (remove non-numeric characters except decimal and negative)
 * @param {string} value - Input value
 * @returns {string} Cleaned value
 */
export const formatNumberInput = (value) => {
  if (!value) return '';

  // Remove everything except numbers, decimal point, and negative sign
  let cleaned = value.toString().replace(/[^0-9.-]/g, '');

  // Ensure only one decimal point
  const parts = cleaned.split('.');
  if (parts.length > 2) {
    cleaned = parts[0] + '.' + parts.slice(1).join('');
  }

  // Ensure negative sign is only at the beginning
  if (cleaned.includes('-')) {
    const isNegative = cleaned.startsWith('-');
    cleaned = cleaned.replace(/-/g, '');
    if (isNegative) {
      cleaned = '-' + cleaned;
    }
  }

  return cleaned;
};

/**
 * Parse currency input to number
 * @param {string} value - Currency string
 * @returns {number} Parsed number
 */
export const parseCurrency = (value) => {
  if (!value) return null;

  // Remove currency symbols, commas, and spaces
  const cleaned = value.toString().replace(/[$,\s]/g, '');

  const number = parseFloat(cleaned);

  return isNaN(number) ? null : number;
};
