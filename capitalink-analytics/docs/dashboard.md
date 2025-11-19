# Dashboard User Guide

## Overview

The Capitalink Analytics Dashboard provides a web-based interface for viewing analytics and metrics across all Capitalink modules.

## Accessing the Dashboard

Navigate to:

```
http://localhost:8008/dashboard
```

Or in production:

```
https://analytics.capitalink.com/dashboard
```

## Dashboard Pages

### Main Dashboard

**URL:** `/dashboard`

The main dashboard provides a high-level overview of all analytics:

**Sections:**

1. **CRM Overview**
   - Total contacts (sellers/buyers)
   - Total companies
   - Listing counts (total and active)

2. **Exit Ready Pipeline**
   - Total cases
   - Cases by status (table)
   - Link to detailed Exit Ready analytics

3. **Facilitator Summary**
   - Total engagements
   - Revenue breakdown (offer fees, success fees)
   - Engagement status distribution
   - Link to detailed Facilitator analytics

**Features:**
- KPI cards with key metrics
- Status distribution tables
- Real-time data (refreshes on page load)
- Timestamp showing last update

### Exit Ready Analytics

**URL:** `/dashboard/exit-ready`

Detailed analytics for the Exit Ready assessment module.

**Sections:**

1. **Pipeline Summary**
   - Total cases
   - Cases by status with percentages

2. **Stage Durations**
   - Average time in each stage
   - Median, min, max durations
   - Sample sizes

3. **Case Volume Over Time**
   - Monthly breakdown
   - Cases created, delivered, and closed

**Use Cases:**
- Monitor Exit Ready pipeline health
- Identify bottlenecks in the process
- Track completion rates
- Analyze processing times

### Facilitator Analytics

**URL:** `/dashboard/facilitator`

Detailed analytics for the Facilitator M&A advisory module.

**Sections:**

1. **Revenue Summary**
   - Total revenue (offer fees + success fees)
   - Offer fees collected
   - Success fees (gross and net)
   - Number of successful closings

2. **Engagement Status Distribution**
   - Engagements by status
   - Status percentages
   - Visual indicators (badges)

3. **Buyer Introduction Funnel**
   - Total introduced buyers
   - Progression through stages
   - Conversion rates between stages

**Use Cases:**
- Track revenue performance
- Monitor engagement pipeline
- Analyze buyer conversion rates
- Identify opportunities for improvement

## Navigation

**Navigation Bar:**
- Dashboard (main overview)
- Exit Ready (detailed analytics)
- Facilitator (detailed analytics)

**Breadcrumb Navigation:**
- Current page highlighted in navigation
- Easy switching between sections

## Features

### KPI Cards

Large, easy-to-read metric cards showing:
- Metric name
- Current value
- Optional context (e.g., "5% of sale price")

### Data Tables

Clean, organized tables with:
- Column headers
- Row highlighting on hover
- Sorted data
- Percentage calculations

### Status Badges

Color-coded badges for different statuses:
- **Green** – Success/Active
- **Blue** – In Progress/Info
- **Gray** – Closed/Inactive
- **Yellow** – Warning/Pending

### Timestamps

Each page shows last update time:
```
Last updated: 2025-01-15 14:23:45
```

## Responsive Design

The dashboard is optimized for:
- Desktop browsers (1024px and up)
- Tablet devices (768px to 1024px)
- Mobile devices (up to 768px)

## Browser Compatibility

Tested and supported on:
- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

## Performance

### Loading Times

- Initial page load: < 2 seconds
- Data refresh: < 1 second
- No caching by default (always fresh data)

### Data Freshness

- Data is queried in real-time from databases
- No stale cached data
- Refresh page to see latest metrics

## Customization

### Themes

Currently uses a single professional theme with:
- Dark blue header (#2c3e50)
- Clean white content areas
- Subtle shadows and borders
- Professional color palette

### Future Enhancements

Planned improvements:
- Dark mode toggle
- Custom date range selectors
- Interactive charts (Chart.js)
- Export to PDF/Excel
- Auto-refresh intervals
- User preferences

## Security

### Access Control

Currently, the dashboard has **no authentication**.

**Recommended for production:**
- Add authentication middleware
- Implement role-based access control
- Use HTTPS only
- Add session management

### Data Privacy

- No PII displayed in aggregated views
- Metrics are aggregated and anonymized
- No raw contact or company data exposed

## Troubleshooting

### Dashboard Not Loading

1. Check if server is running:
   ```bash
   curl http://localhost:8008/api/v1/health
   ```

2. Check browser console for errors

3. Verify database connections in `.env`

### Slow Loading

Causes:
- Large datasets in upstream databases
- Network latency to database servers
- Complex aggregation queries

Solutions:
- Optimize database queries
- Add database indexes
- Use connection pooling
- Enable result caching (future)

### Incorrect Data

1. Verify upstream database connections
2. Check data in upstream databases directly
3. Review analytics service logic
4. Check logs for errors

### Layout Issues

- Clear browser cache
- Disable browser extensions
- Try different browser
- Check screen resolution

## Tips for Best Experience

1. **Use latest browser** for best performance
2. **Larger screens** provide better data visibility
3. **Bookmark frequently used pages** for quick access
4. **Refresh regularly** for latest data
5. **Use CLI or API** for automated reporting

## Keyboard Shortcuts

Currently no keyboard shortcuts implemented.

**Planned:**
- `R` – Refresh current page
- `D` – Go to main dashboard
- `E` – Go to Exit Ready analytics
- `F` – Go to Facilitator analytics

## Mobile Experience

While responsive, the dashboard is optimized for desktop use due to:
- Data-heavy tables
- Multiple KPI cards
- Wide layouts

**Recommendations:**
- Use tablet or desktop for best experience
- Mobile devices can view but may require horizontal scrolling
- Consider API or CLI for mobile contexts

## Exporting Data

Current dashboard does not support data export.

**Alternatives:**
- Use API endpoints for programmatic access
- Use CLI for terminal-based reporting
- Use browser print to PDF
- Screenshot for presentations

## Feedback and Improvements

The dashboard is designed to be simple and functional. Future enhancements welcome:
- Interactive charts and graphs
- Drill-down capabilities
- Custom filters and date ranges
- Saved views and bookmarks
- Email reports
- Dashboard sharing
