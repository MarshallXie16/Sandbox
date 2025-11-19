# CLI Usage Guide

## Overview

The Facilitator CLI provides operator-friendly commands for managing engagements, buyers, offers, and closings from the command line.

## Installation

```bash
cd facilitator-automation
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Ensure `.env` is configured with `DATABASE_URL`.

## General Usage

```bash
python cli.py [COMMAND GROUP] [COMMAND] [OPTIONS]
```

Get help:
```bash
python cli.py --help
python cli.py engagements --help
python cli.py buyers --help
```

---

## Engagement Commands

### List Engagements

```bash
python cli.py engagements list

# Filter by status
python cli.py engagements list --status active
python cli.py engagements list --status closed_success

# Filter by seller
python cli.py engagements list --seller-contact-id 123
```

**Output:**
```
┏━━━━┳━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━┳━━━━━━━━━━━┳━━━━━━━━━━━━┓
┃ ID ┃ Code          ┃ Status         ┃ Seller ID ┃ Created    ┃
┡━━━━╇━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━╇━━━━━━━━━━━╇━━━━━━━━━━━━┩
│ 1  │ FAC-2025-0001 │ active         │ 123       │ 2025-01-19 │
│ 2  │ FAC-2025-0002 │ offers_in_play │ 456       │ 2025-01-20 │
└────┴───────────────┴────────────────┴───────────┴────────────┘
```

### Create Engagement

```bash
python cli.py engagements create \
  --seller-contact-id 123 \
  --company-id 456 \
  --listing-id 789
```

**Output:**
```
Created engagement FAC-2025-0003 (ID: 3)
```

### Activate Engagement

```bash
python cli.py engagements activate 1
```

**Output:**
```
Activated engagement FAC-2025-0001 (status: active)
```

### View Engagement Summary

```bash
python cli.py engagements summary 1
```

**Output:**
```
Engagement FAC-2025-0001
Status: offers_in_play
Seller Contact ID: 123
Offer Fee: $5,000.00
Success Fee Rate: 5.0%

Introduced Buyers: 3
Offers: 2
Closings: 0
```

---

## Buyer Commands

### Introduce Buyer

```bash
python cli.py buyers add \
  --engagement-id 1 \
  --buyer-contact-id 321 \
  --channel email
```

**Channels:** email, phone, event, referral, direct, other

**Output:**
```
Introduced buyer 321 to engagement 1 (buyer_intro_id: 1)
```

### List Buyers

```bash
python cli.py buyers list 1
```

**Output:**
```
┏━━━━┳━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━┳━━━━━━━━━┳━━━━━━━━━━━━┓
┃ ID ┃ Buyer Contact ID ┃ Status    ┃ Channel ┃ Introduced ┃
┡━━━━╇━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━╇━━━━━━━━━╇━━━━━━━━━━━━┩
│ 1  │ 321             │ nda_signed│ email   │ 2025-01-19 │
│ 2  │ 322             │ invited   │ phone   │ 2025-01-20 │
└────┴─────────────────┴───────────┴─────────┴────────────┘
```

### Set Buyer Status

```bash
python cli.py buyers set-status 1 nda_signed
```

**Valid statuses:**
- invited
- nda_pending
- nda_signed
- teaser_sent
- info_access
- offer_made
- inactive
- not_interested
- dropped

**Output:**
```
Updated buyer intro 1 status to nda_signed
```

---

## Offer Commands

### Record Offer

```bash
python cli.py offers add \
  --engagement-id 1 \
  --buyer-intro-id 1 \
  --headline-price 2500000
```

**Output:**
```
Recorded offer 1: $2,500,000.00 from buyer_intro 1
```

### List Offers

```bash
python cli.py offers list 1
```

**Output:**
```
┏━━━━┳━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━┳━━━━━━━━━━━┓
┃ ID ┃ Buyer Intro ID ┃ Price        ┃ Status       ┃ Offer Fee ┃
┡━━━━╇━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━╇━━━━━━━━━━━┩
│ 1  │ 1             │ $2,500,000.00│ received     │ $5,000.00 │
│ 2  │ 2             │ $2,750,000.00│ under_review │ $5,000.00 │
└────┴───────────────┴──────────────┴──────────────┴───────────┘
```

---

## Closing Commands

### Record Closing

```bash
python cli.py closings record \
  --engagement-id 1 \
  --buyer-intro-id 1 \
  --final-price 2500000
```

**Output:**
```
Closing Recorded Successfully!
Closing ID: 1
Final Price: $2,500,000.00

Fee Calculation:
  Success Fee Rate: 5.0%
  Gross Success Fee: $125,000.00
  Offer Fee Credit: -$5,000.00
  Net Success Fee: $120,000.00
```

### Show Closing

```bash
python cli.py closings show 1
```

**Output:**
```
Closing for Engagement 1
Closing Date: 2025-04-01
Final Price: $2,500,000.00
Buyer Intro ID: 1

Fees:
  Gross: $125,000.00
  Credit: $5,000.00
  Net: $120,000.00

Status:
  Invoiced: No
  Paid: No
```

---

## Complete Workflow Example

```bash
# 1. Create engagement
python cli.py engagements create \
  --seller-contact-id 123 \
  --company-id 456 \
  --listing-id 789

# Output: Created engagement FAC-2025-0001 (ID: 1)

# 2. Activate engagement
python cli.py engagements activate 1

# 3. Introduce buyers
python cli.py buyers add \
  --engagement-id 1 \
  --buyer-contact-id 321 \
  --channel email

python cli.py buyers add \
  --engagement-id 1 \
  --buyer-contact-id 322 \
  --channel phone

# 4. Track buyer progress
python cli.py buyers set-status 1 nda_signed
python cli.py buyers set-status 1 teaser_sent
python cli.py buyers set-status 1 offer_made

# 5. Record offer
python cli.py offers add \
  --engagement-id 1 \
  --buyer-intro-id 1 \
  --headline-price 2500000

# 6. View engagement summary
python cli.py engagements summary 1

# 7. Record closing
python cli.py closings record \
  --engagement-id 1 \
  --buyer-intro-id 1 \
  --final-price 2500000

# 8. View closing details
python cli.py closings show 1
```

---

## Tips & Best Practices

### Database Connection
Ensure `.env` has correct `DATABASE_URL`:
```
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/facilitator_db
```

### Tab Completion
For better CLI experience, consider using tab completion:
```bash
# Install
pip install argcomplete

# Enable
eval "$(register-python-argcomplete cli.py)"
```

### Rich Output
The CLI uses Rich library for formatted tables. For best experience:
- Use a terminal with color support
- Set terminal width ≥ 100 columns

### Error Handling
If commands fail, check:
1. Database connection (verify `DATABASE_URL`)
2. Migrations are up to date (`make upgrade`)
3. Valid IDs (engagement, buyer_intro, etc.)
4. State transitions (e.g., can't close a draft engagement)

---

## Scripting & Automation

CLI commands can be scripted:

```bash
#!/bin/bash
# Bulk introduce buyers

ENGAGEMENT_ID=1
BUYER_IDS=(321 322 323 324 325)

for buyer_id in "${BUYER_IDS[@]}"; do
  python cli.py buyers add \
    --engagement-id $ENGAGEMENT_ID \
    --buyer-contact-id $buyer_id \
    --channel email

  echo "Introduced buyer $buyer_id"
  sleep 0.5
done

echo "All buyers introduced!"
```

---

For API access, see [API Usage Guide](api_usage.md).
