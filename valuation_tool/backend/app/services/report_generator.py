"""Report Generator - Generate Full Valuation reports in Markdown format."""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import UUID
from datetime import datetime

from app.models.project import Project
from app.models.valuation_summary import ValuationSummary
from app.models.dcf_result import DCFResult
from app.models.dcf_parameter import DCFParameter
from app.models.dcf_cash_flow import DCFCashFlow
from app.models.full_valuation_summary import FullValuationSummary
from app.models.normalized_financial import NormalizedFinancial
from app.models.normalization_entry import NormalizationEntry


async def generate_full_valuation_report(
    db: AsyncSession,
    project_id: UUID
) -> str:
    """
    Generate a comprehensive Full Valuation report in Markdown format.

    The report includes:
    - Executive Summary
    - Business Overview
    - Financial Recast/Normalization
    - Market Approach Valuation
    - DCF Approach Valuation
    - Weighted Final Valuation
    - Appendices

    Returns:
        Markdown-formatted report as a string
    """
    # Load all necessary data
    result = await db.execute(
        select(Project).where(Project.id == project_id)
    )
    project = result.scalar_one_or_none()

    if not project:
        raise ValueError(f"Project {project_id} not found")

    # Load other data
    valuation_summary = await _load_optional(db, ValuationSummary, project_id)
    dcf_result = await _load_optional(db, DCFResult, project_id)
    dcf_params = await _load_optional(db, DCFParameter, project_id)
    full_summary = await _load_optional(db, FullValuationSummary, project_id)

    # Load lists
    normalized_financials = await _load_list(db, NormalizedFinancial, project_id)
    normalization_entries = await _load_list(db, NormalizationEntry, project_id)
    dcf_cash_flows = await _load_list(db, DCFCashFlow, project_id)

    # Generate report sections
    report_date = datetime.now().strftime("%B %d, %Y")

    report = f"""# BUSINESS VALUATION REPORT

**Company:** {project.business_name}
**Industry:** {project.industry}
**Report Date:** {report_date}
**Project:** {project.project_name}

---

## EXECUTIVE SUMMARY

This report presents a comprehensive valuation analysis of {project.business_name}, incorporating multiple valuation methodologies to arrive at a fair market value estimate.

"""

    # Add Full Valuation Summary if available
    if full_summary:
        report += f"""### Valuation Conclusion

| Approach | Weight | Value |
|----------|--------|-------|
| Market Approach | {float(full_summary.weight_market) * 100:.1f}% | {_format_currency(full_summary.market_value_mid, project.currency)} |
| DCF Approach | {float(full_summary.weight_dcf) * 100:.1f}% | {_format_currency(full_summary.dcf_value, project.currency)} |
| Asset Approach | {float(full_summary.weight_asset) * 100:.1f}% | {_format_currency(full_summary.asset_value, project.currency)} |

**Final Valuation Range:**

- **Low:** {_format_currency(full_summary.final_value_low, project.currency)}
- **Mid (Fair Market Value):** {_format_currency(full_summary.final_value_mid, project.currency)}
- **High:** {_format_currency(full_summary.final_value_high, project.currency)}

"""

    # Business Overview
    report += f"""---

## 1. BUSINESS OVERVIEW

**Business Name:** {project.business_name}
**Industry:** {project.industry}
**Currency:** {project.currency}

"""

    if project.description:
        report += f"**Description:**\n{project.description}\n\n"

    # Normalized Financials
    if normalized_financials or normalization_entries:
        report += """---

## 2. FINANCIAL NORMALIZATION (RECAST)

### Purpose
Financial normalization adjusts reported historical financials to reflect the true economic earnings of the business by removing non-recurring, owner-specific, or discretionary expenses.

"""

        if normalization_entries:
            report += "### Normalization Adjustments\n\n"
            for entry in sorted(normalization_entries, key=lambda x: x.year):
                adjustment_type = "Addback" if entry.is_addback else "Reduction"
                report += f"**{entry.year} - {entry.category}** ({adjustment_type})\n"
                report += f"- Amount: {_format_currency(entry.amount, project.currency)}\n"
                report += f"- Description: {entry.description}\n\n"

        if normalized_financials:
            report += "### Normalized Financials Summary\n\n"
            report += "| Year | Revenue | EBITDA | SDE | Net Income |\n"
            report += "|------|---------|--------|-----|------------|\n"

            for nf in sorted(normalized_financials, key=lambda x: x.year):
                report += f"| {nf.year} | {_format_currency(nf.normalized_revenue, project.currency)} | "
                report += f"{_format_currency(nf.normalized_ebitda, project.currency)} | "
                report += f"{_format_currency(nf.normalized_sde, project.currency)} | "
                report += f"{_format_currency(nf.normalized_net_income, project.currency)} |\n"

            report += "\n"

    # Market Approach
    if valuation_summary:
        report += """---

## 3. MARKET APPROACH VALUATION

### Methodology
The Market Approach estimates value based on industry-specific multiples applied to a key earnings metric. This approach reflects what similar businesses in the market are trading for.

"""

        report += f"""### Valuation Calculation

**Method:** {valuation_summary.method.replace('_', ' ').title()}
**Base Metric:** {valuation_summary.base_metric_type} = {_format_currency(valuation_summary.base_metric_value, project.currency)}

| Multiple Range | Multiple | Business Value |
|----------------|----------|----------------|
| Low | {float(valuation_summary.multiple_low):.2f}x | {_format_currency(valuation_summary.value_low, project.currency)} |
| Mid | {float(valuation_summary.multiple_mid):.2f}x | {_format_currency(valuation_summary.value_mid, project.currency)} |
| High | {float(valuation_summary.multiple_high):.2f}x | {_format_currency(valuation_summary.value_high, project.currency)} |

**Market Approach Conclusion:** {_format_currency(valuation_summary.value_mid, project.currency)}

"""

    # DCF Approach
    if dcf_result and dcf_params:
        report += """---

## 4. DISCOUNTED CASH FLOW (DCF) APPROACH

### Methodology
The DCF Approach values the business based on the present value of projected future cash flows, discounted at an appropriate rate that reflects the risk of the investment.

"""

        report += f"""### DCF Parameters

- **Base Metric:** {dcf_params.base_metric}
- **Base Year:** {dcf_params.base_year}
- **Discount Rate:** {float(dcf_params.discount_rate) * 100:.2f}%
- **Projection Period:** {dcf_params.projection_years} years
- **Terminal Method:** {dcf_params.terminal_method.replace('_', ' ').title()}
"""

        if dcf_params.terminal_method == 'terminal_growth':
            report += f"- **Terminal Growth Rate:** {float(dcf_params.terminal_growth_rate or 0) * 100:.2f}%\n"
        else:
            report += f"- **Exit Multiple:** {float(dcf_params.terminal_multiple or 0):.2f}x\n"

        report += "\n"

        if dcf_cash_flows:
            report += "### Projected Cash Flows\n\n"
            report += "| Year | Cash Flow | Discounted CF |\n"
            report += "|------|-----------|---------------|\n"

            for cf in dcf_cash_flows:
                report += f"| {cf.year_label} | {_format_currency(cf.cash_flow, project.currency)} | "
                report += f"{_format_currency(cf.discounted_cash_flow, project.currency)} |\n"

            report += "\n"

        report += f"""### DCF Valuation Summary

| Component | Value |
|-----------|-------|
| Present Value of Cash Flows | {_format_currency(dcf_result.present_value_of_cash_flows, project.currency)} |
| Terminal Value | {_format_currency(dcf_result.terminal_value, project.currency)} |
| PV of Terminal Value | {_format_currency(dcf_result.present_value_of_terminal_value, project.currency)} |
| **DCF Equity Value** | **{_format_currency(dcf_result.dcf_equity_value, project.currency)}** |

"""

    # Weighted Conclusion
    if full_summary:
        report += """---

## 5. WEIGHTED VALUATION CONCLUSION

### Methodology
The final valuation combines multiple approaches using appropriate weights based on the reliability, applicability, and quality of data for each method.

"""

        report += f"""### Weighting Rationale

- **Market Approach ({float(full_summary.weight_market) * 100:.0f}%):** Industry multiples provide a market-based benchmark
- **DCF Approach ({float(full_summary.weight_dcf) * 100:.0f}%):** Forward-looking cash flow projections
- **Asset Approach ({float(full_summary.weight_asset) * 100:.0f}%):** {
    "Asset-based value" if full_summary.asset_value else "Not applicable for this business"
}

### Final Valuation Range

| Range | Value |
|-------|-------|
| **Low** | **{_format_currency(full_summary.final_value_low, project.currency)}** |
| **Mid (Fair Market Value)** | **{_format_currency(full_summary.final_value_mid, project.currency)}** |
| **High** | **{_format_currency(full_summary.final_value_high, project.currency)}** |

"""

    # Disclaimers
    report += """---

## IMPORTANT DISCLAIMERS

This valuation report is for informational purposes only and should not be relied upon as the sole basis for any financial, legal, tax, or business decisions.

### Limitations

- This analysis is based on financial information provided and assumed to be accurate
- Market conditions, industry trends, and company-specific factors can change rapidly
- Actual transaction values may differ materially from valuation estimates
- This report does not constitute a recommendation to buy, sell, or hold any interest

### Professional Advice

For important decisions, please consult with qualified professionals:
- Certified Business Valuator (CBV) or Accredited Senior Appraiser (ASA)
- Certified Public Accountant (CPA)
- Legal counsel
- M&A advisor

---

**End of Report**

*Generated by Exit Builder Platform*
*Report Date: {report_date}*
"""

    return report


async def _load_optional(db: AsyncSession, model_class, project_id: UUID):
    """Load a single optional record."""
    result = await db.execute(
        select(model_class).where(model_class.project_id == project_id)
    )
    return result.scalar_one_or_none()


async def _load_list(db: AsyncSession, model_class, project_id: UUID):
    """Load a list of records."""
    result = await db.execute(
        select(model_class).where(model_class.project_id == project_id)
    )
    return result.scalars().all()


def _format_currency(value, currency: str = "CAD") -> str:
    """Format a numeric value as currency."""
    if value is None:
        return "N/A"

    # Convert to float for formatting
    value_float = float(value)

    # Format with commas and 2 decimal places
    if currency == "CAD":
        return f"${value_float:,.2f} CAD"
    elif currency == "USD":
        return f"${value_float:,.2f} USD"
    else:
        return f"{value_float:,.2f} {currency}"
