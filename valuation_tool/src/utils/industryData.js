/**
 * Industry-specific valuation multipliers
 * Sources: BizBuySell, Business Valuation Resources, industry reports
 *
 * Each industry has multipliers for:
 * - Revenue (annual sales)
 * - EBITDA (earnings before interest, taxes, depreciation, amortization)
 *
 * Ranges represent typical valuations:
 * - low: Conservative estimate
 * - average: Typical market rate
 * - high: Premium businesses with strong fundamentals
 */

export const INDUSTRIES = [
  {
    id: 'saas',
    name: 'SaaS / Software',
    revenueMultiplier: {
      low: 4.0,
      average: 6.0,
      high: 10.0
    },
    ebitdaMultiplier: {
      low: 8.0,
      average: 12.0,
      high: 20.0
    },
    description: 'Software as a Service and technology companies'
  },
  {
    id: 'ecommerce',
    name: 'E-commerce',
    revenueMultiplier: {
      low: 1.5,
      average: 2.5,
      high: 4.0
    },
    ebitdaMultiplier: {
      low: 5.0,
      average: 7.0,
      high: 10.0
    },
    description: 'Online retail and digital marketplaces'
  },
  {
    id: 'professional_services',
    name: 'Professional Services',
    revenueMultiplier: {
      low: 0.75,
      average: 1.5,
      high: 3.0
    },
    ebitdaMultiplier: {
      low: 3.0,
      average: 5.0,
      high: 8.0
    },
    description: 'Consulting, legal, accounting, marketing agencies'
  },
  {
    id: 'manufacturing',
    name: 'Manufacturing',
    revenueMultiplier: {
      low: 0.8,
      average: 1.5,
      high: 2.5
    },
    ebitdaMultiplier: {
      low: 4.0,
      average: 6.0,
      high: 9.0
    },
    description: 'Production and manufacturing businesses'
  },
  {
    id: 'retail',
    name: 'Retail',
    revenueMultiplier: {
      low: 0.3,
      average: 0.75,
      high: 1.5
    },
    ebitdaMultiplier: {
      low: 3.0,
      average: 5.0,
      high: 7.0
    },
    description: 'Brick-and-mortar retail stores'
  },
  {
    id: 'restaurant',
    name: 'Restaurant / Food Service',
    revenueMultiplier: {
      low: 0.25,
      average: 0.5,
      high: 1.0
    },
    ebitdaMultiplier: {
      low: 2.0,
      average: 3.5,
      high: 5.0
    },
    description: 'Restaurants, cafes, food service businesses'
  },
  {
    id: 'healthcare',
    name: 'Healthcare / Medical',
    revenueMultiplier: {
      low: 0.8,
      average: 1.5,
      high: 2.5
    },
    ebitdaMultiplier: {
      low: 5.0,
      average: 7.0,
      high: 10.0
    },
    description: 'Medical practices, healthcare services'
  },
  {
    id: 'construction',
    name: 'Construction / Contracting',
    revenueMultiplier: {
      low: 0.5,
      average: 1.0,
      high: 1.8
    },
    ebitdaMultiplier: {
      low: 3.0,
      average: 5.0,
      high: 7.0
    },
    description: 'Construction, contracting, trades'
  },
  {
    id: 'real_estate',
    name: 'Real Estate Services',
    revenueMultiplier: {
      low: 1.0,
      average: 2.0,
      high: 3.5
    },
    ebitdaMultiplier: {
      low: 4.0,
      average: 6.0,
      high: 9.0
    },
    description: 'Real estate agencies, property management'
  },
  {
    id: 'other',
    name: 'Other / General Business',
    revenueMultiplier: {
      low: 0.5,
      average: 1.0,
      high: 2.0
    },
    ebitdaMultiplier: {
      low: 3.0,
      average: 5.0,
      high: 7.0
    },
    description: 'General business not fitting other categories'
  }
];

/**
 * Get industry data by ID
 * @param {string} industryId - The industry identifier
 * @returns {object|null} Industry data object or null if not found
 */
export const getIndustryById = (industryId) => {
  return INDUSTRIES.find(industry => industry.id === industryId) || null;
};

/**
 * Get all industry names for dropdown
 * @returns {array} Array of {id, name} objects
 */
export const getIndustryOptions = () => {
  return INDUSTRIES.map(industry => ({
    id: industry.id,
    name: industry.name
  }));
};

/**
 * Get multiplier based on business characteristics
 * @param {object} industry - Industry data object
 * @param {string} type - 'revenue' or 'ebitda'
 * @param {object} businessData - Business data for adjustments
 * @returns {number} Calculated multiplier
 */
export const getAdjustedMultiplier = (industry, type, businessData = {}) => {
  if (!industry) return 1;

  const multiplierKey = type === 'revenue' ? 'revenueMultiplier' : 'ebitdaMultiplier';
  const baseMultiplier = industry[multiplierKey].average;

  let adjustedMultiplier = baseMultiplier;

  // Adjust for revenue growth
  if (businessData.revenueGrowthRate) {
    const growthRate = parseFloat(businessData.revenueGrowthRate) || 0;

    if (growthRate > 20) {
      // High growth: increase multiplier by 15%
      adjustedMultiplier *= 1.15;
    } else if (growthRate > 10) {
      // Moderate growth: increase by 8%
      adjustedMultiplier *= 1.08;
    } else if (growthRate < -5) {
      // Declining: decrease by 15%
      adjustedMultiplier *= 0.85;
    }
  }

  // Adjust for company age/stability
  if (businessData.yearsFounded) {
    const years = parseInt(businessData.yearsFounded) || 0;

    if (years >= 10) {
      // Established business: increase by 8%
      adjustedMultiplier *= 1.08;
    } else if (years >= 5) {
      // Moderately established: increase by 4%
      adjustedMultiplier *= 1.04;
    } else if (years < 2) {
      // Very new: decrease by 10%
      adjustedMultiplier *= 0.90;
    }
  }

  // Ensure we stay within reasonable bounds
  const maxMultiplier = industry[multiplierKey].high;
  const minMultiplier = industry[multiplierKey].low;

  adjustedMultiplier = Math.max(minMultiplier, Math.min(maxMultiplier, adjustedMultiplier));

  return adjustedMultiplier;
};

export default INDUSTRIES;
