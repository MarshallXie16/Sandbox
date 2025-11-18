# Business Valuation Calculator

A simple, React-based web application that helps entrepreneurs, small business owners, and investors quickly estimate the value of a business using established valuation methodologies.

![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

## Features

- **Three Valuation Methods**
  - Revenue Multiple Method
  - EBITDA Multiple Method
  - Asset-Based Method

- **Industry-Specific Multipliers**
  - 10+ industry categories with research-backed multipliers
  - Automatic adjustments based on growth rate and company age

- **Comprehensive Results**
  - Detailed calculation breakdowns
  - Confidence level indicators
  - Method comparison view
  - Valuation range estimates

- **User-Friendly Interface**
  - Clean, modern design
  - Responsive (mobile, tablet, desktop)
  - Real-time validation
  - Educational tooltips

## Quick Start

### Prerequisites

- Node.js 16+ and npm

### Installation

```bash
# Clone or download the repository
cd valuation_tool

# Install dependencies
npm install

# Start development server
npm run dev
```

The application will be available at `http://localhost:5173`

### Build for Production

```bash
# Create optimized production build
npm run build

# Preview production build
npm run preview
```

## Usage

### Step 1: Select Valuation Method

Choose from three valuation methodologies:

- **Revenue Multiple**: Best for businesses with consistent revenue (e.g., SaaS, e-commerce)
- **EBITDA Multiple**: Preferred for profitable businesses with good margins
- **Asset-Based**: Ideal for asset-heavy businesses or those with negative earnings

### Step 2: Enter Business Information

Fill in your business details:

**Required:**
- Business Name
- Industry
- Annual Revenue

**Optional (but recommended for better accuracy):**
- Annual Net Profit
- EBITDA
- Total Assets
- Total Liabilities
- Revenue Growth Rate
- Years in Business

### Step 3: Calculate & Review

Click "Calculate Business Value" to see:
- Estimated business value
- Confidence level (low/medium/high)
- Detailed calculation breakdown
- Comparison across all applicable methods
- Valuation range

### Example

For a SaaS company with:
- Annual Revenue: $500,000
- EBITDA: $100,000
- Growth Rate: 20%
- Years Founded: 5

The calculator will provide:
- Revenue Multiple estimate (~$3.0M - $4.0M)
- EBITDA Multiple estimate (~$1.2M - $1.8M)
- Detailed explanations for each method

## Project Structure

```
valuation_tool/
├── src/
│   ├── components/          # React components
│   │   ├── ValuationForm.jsx
│   │   ├── ValuationForm.css
│   │   ├── ValuationResults.jsx
│   │   └── ValuationResults.css
│   ├── utils/              # Utility functions
│   │   ├── calculations.js  # Valuation logic
│   │   ├── industryData.js  # Industry multipliers
│   │   └── validators.js    # Input validation
│   ├── App.jsx             # Main component
│   ├── App.css             # Global styles
│   └── main.jsx            # Entry point
├── docs/                   # Documentation
│   ├── business_plan.md
│   ├── product_design.md
│   ├── user_stories.md
│   ├── roadmap.md
│   ├── tasks.md
│   └── memory.md
├── public/                 # Static assets
├── CLAUDE.md              # Development framework
└── package.json
```

## Valuation Methodologies

### Revenue Multiple

**Formula:** `Business Value = Annual Revenue × Industry Multiplier`

Industry multipliers range from 0.25x (restaurants) to 10x (high-growth SaaS).

**Adjustments:**
- +15% for >20% YoY growth
- +8% for >10% YoY growth
- -15% for negative growth
- +8% for 10+ years in business

### EBITDA Multiple

**Formula:** `Business Value = EBITDA × Industry Multiplier`

Typically ranges from 2x to 20x depending on industry and business quality.

**Best When:**
- EBITDA is positive
- EBITDA margin > 15%
- Business is mature and stable

### Asset-Based

**Formula:** `Business Value = (Total Assets - Total Liabilities) × Multiplier`

Multiplier typically 0.7x - 1.3x of book value.

**Best When:**
- Asset-heavy business
- Negative or inconsistent earnings
- Liquidation scenarios

## Industry Multipliers

| Industry | Revenue Multiple | EBITDA Multiple |
|----------|------------------|-----------------|
| SaaS/Software | 4-10x | 8-20x |
| E-commerce | 1.5-4x | 5-10x |
| Professional Services | 0.75-3x | 3-8x |
| Manufacturing | 0.8-2.5x | 4-9x |
| Retail | 0.3-1.5x | 3-7x |
| Restaurant | 0.25-1x | 2-5x |
| Healthcare | 0.8-2.5x | 5-10x |
| Construction | 0.5-1.8x | 3-7x |

*Note: Multipliers based on industry research and market data. Actual valuations vary.*

## Important Disclaimers

This calculator provides **educational estimates only** and should not be used as the sole basis for any financial, legal, or business decisions.

### Limitations

- Simplified methodologies
- Does not account for:
  - Market conditions
  - Competitive positioning
  - Customer concentration
  - Intellectual property value
  - Management quality
  - Many other qualitative factors

### Professional Advice

For any significant business transaction, legal matter, tax purpose, or financial decision, please consult:
- Certified Business Valuator (CBV)
- Certified Public Accountant (CPA)
- Financial Advisor
- M&A Specialist

## Development

### Tech Stack

- **Frontend:** React 18
- **Build Tool:** Vite
- **Styling:** CSS3 (vanilla)
- **State Management:** React Hooks

### Code Quality

- ESLint for code linting
- Modular component structure
- Well-documented functions
- Input validation and sanitization

### Testing

```bash
# Run development server for manual testing
npm run dev

# Build to check for errors
npm run build
```

**Manual Testing Checklist:**
- [ ] Test all three valuation methods
- [ ] Verify calculations with known examples
- [ ] Test input validation (negative numbers, empty fields)
- [ ] Test responsive design (mobile, tablet, desktop)
- [ ] Cross-browser testing (Chrome, Firefox, Safari, Edge)
- [ ] Test edge cases (very large/small numbers)

## Deployment

### Recommended Platforms

- **Netlify** (recommended)
  ```bash
  # Build command
  npm run build

  # Publish directory
  dist
  ```

- **Vercel**
  - Auto-detected configuration
  - Zero config deployment

- **GitHub Pages**
  - Build and deploy to gh-pages branch

### Environment Variables

No environment variables required for MVP.

## Roadmap

See [docs/roadmap.md](docs/roadmap.md) for detailed development timeline.

### Upcoming Features

- Save valuations (requires backend)
- Export as PDF
- Advanced DCF calculator
- Scenario modeling
- User accounts
- API access

## Contributing

This is an educational project. Contributions welcome!

1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

## License

MIT License - see LICENSE file for details

## Support

For issues, questions, or feedback:
- Open an issue on GitHub
- Email: [your-email@example.com]

## Acknowledgments

- Industry multiplier data: BizBuySell, Business Valuation Resources
- Valuation methodologies: Established business valuation practices
- UI inspiration: Modern web design principles

---

**Built with ❤️ for entrepreneurs and business owners**

*Remember: This tool is for preliminary estimates. Always consult professionals for important decisions.*
