# CLI Usage Guide

## Overview

The Capitalink Analytics CLI provides terminal-based access to analytics data and operations.

## Installation

The CLI is included in the main installation:

```bash
pip install -r requirements.txt
```

## Basic Usage

```bash
python cli.py [COMMAND] [OPTIONS]
```

## Commands

### Snapshot Management

#### Run Snapshot

Collect metrics from upstream sources and store in analytics database.

```bash
python cli.py snapshot --date 2025-01-15
```

**Options:**
- `--date, -d` – Snapshot date (YYYY-MM-DD). Defaults to today.
- `--domain` – Specific domain to snapshot: `exit_ready`, `facilitator`, or `crm`

**Examples:**

```bash
# Snapshot all domains for today
python cli.py snapshot

# Snapshot specific date
python cli.py snapshot --date 2025-01-15

# Snapshot only Exit Ready domain
python cli.py snapshot --date 2025-01-15 --domain exit_ready
```

### Exit Ready Analytics

#### Summary Report

Display Exit Ready analytics summary with pipeline status and stage durations.

```bash
python cli.py exit-ready
```

**Output:**
```
Exit Ready Analytics Summary

┏━━━━━━━━━━━━━━━━━━━┳━━━━━━━┳━━━━━━━━━━━┓
┃ Status            ┃ Count ┃ Percentage┃
┡━━━━━━━━━━━━━━━━━━━╇━━━━━━━╇━━━━━━━━━━━┩
│ Created           │    3  │      7.1% │
│ Intake Pending    │    5  │     11.9% │
│ Docs Collecting   │    7  │     16.7% │
│ Valuation Done    │   10  │     23.8% │
│ Report Ready      │    4  │      9.5% │
│ Delivered         │    9  │     21.4% │
│ Closed            │    4  │      9.5% │
├───────────────────┼───────┼───────────┤
│ Total             │   42  │    100.0% │
└───────────────────┴───────┴───────────┘

Stage Durations

┏━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━━━━━━━┓
┃ Stage              ┃ Avg Days ┃ Median Days┃ Sample Size ┃
┡━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━━━━━╇━━━━━━━━━━━━━┩
│ Created To Intake  │     5.2  │        4.0 │          38 │
│ Intake To Docs     │     8.5  │        7.0 │          35 │
│ ...                │      ... │        ... │         ... │
└────────────────────┴──────────┴────────────┴─────────────┘
```

### Facilitator Analytics

#### Revenue Report

Display Facilitator revenue summary with breakdown by fee type.

```bash
python cli.py facilitator revenue
```

**Options:**
- `--from` – Start date (YYYY-MM-DD)
- `--to` – End date (YYYY-MM-DD)

**Examples:**

```bash
# All-time revenue
python cli.py facilitator revenue

# Revenue for specific period
python cli.py facilitator revenue --from 2025-01-01 --to 2025-01-31

# Revenue for Q1 2025
python cli.py facilitator revenue --from 2025-01-01 --to 2025-03-31
```

**Output:**
```
Facilitator Revenue Summary (2025-01-01 to 2025-01-31)

┏━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━┓
┃ Metric               ┃        Value ┃
┡━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━┩
│ Offer Fees           │  $25,000.00  │
│ Success Fee (Gross)  │ $450,000.00  │
│ Success Fee (Net)    │ $425,000.00  │
├──────────────────────┼──────────────┤
│ Total Revenue        │ $450,000.00  │
├──────────────────────┼──────────────┤
│ Successful Closings  │           5  │
└──────────────────────┴──────────────┘
```

#### Buyer Funnel

Display buyer introduction funnel with conversion rates.

```bash
python cli.py facilitator funnel
```

**Output:**
```
Facilitator Buyer Introduction Funnel

┏━━━━━━━━━━━━━━━┳━━━━━━━┳━━━━━━━━━━━━━━━━━┓
┃ Stage         ┃ Count ┃ Conversion Rate ┃
┡━━━━━━━━━━━━━━━╇━━━━━━━╇━━━━━━━━━━━━━━━━━┩
│ Introduced    │   150 │               - │
│ Nda Signed    │    95 │           63.3% │
│ Teaser Sent   │    80 │           84.2% │
│ Info Access   │    45 │           56.3% │
│ Offer         │    18 │           40.0% │
│ Closing       │     5 │           27.8% │
└───────────────┴───────┴─────────────────┘
```

### CRM Analytics

#### Overview

Display CRM overview statistics.

```bash
python cli.py crm
```

**Output:**
```
CRM Overview

┏━━━━━━━━━━━━━━━━━┳━━━━━━━┓
┃ Metric          ┃ Value ┃
┡━━━━━━━━━━━━━━━━━╇━━━━━━━┩
│ Total Contacts  │  1250 │
│   - Sellers     │   450 │
│   - Buyers      │   800 │
├─────────────────┼───────┤
│ Total Companies │   380 │
├─────────────────┼───────┤
│ Total Listings  │   125 │
│ Active Listings │    68 │
└─────────────────┴───────┘
```

## Help

Get help for any command:

```bash
python cli.py --help
python cli.py snapshot --help
python cli.py facilitator --help
```

## Output Formats

All CLI output uses Rich library for:
- Formatted tables
- Color-coded output
- Progress indicators
- Clean terminal layout

## Scheduling Snapshots

Use cron to schedule regular snapshots:

```bash
# Run daily snapshot at 2 AM
0 2 * * * cd /path/to/capitalink-analytics && /path/to/venv/bin/python cli.py snapshot
```

## Logging

CLI operations are logged to standard output. Redirect to file if needed:

```bash
python cli.py snapshot 2>&1 | tee snapshot.log
```

## Exit Codes

- `0` – Success
- `1` – Error (check output for details)

## Troubleshooting

### Database Connection Errors

Ensure `.env` is properly configured with database URLs:

```bash
cat .env | grep DATABASE_URL
```

### Permission Errors

Ensure database user has read permissions on upstream databases.

### Slow Queries

For large datasets, queries may take time. Consider:
- Using date filters
- Running during off-peak hours
- Optimizing database indexes
