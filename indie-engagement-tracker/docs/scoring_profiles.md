# Scoring Profiles

Scoring profiles define how engagement scores are calculated. This document explains the structure and provides examples.

## Profile Structure

A scoring profile consists of:

```json
{
  "name": "Profile Name",
  "description": "Description of the profile",
  "rules": {
    "event_weights": {
      "event_type_1": weight_value,
      "event_type_2": weight_value
    },
    "time_decay": {
      "enabled": true,
      "decay_days": 90,
      "decay_factor": 0.5
    }
  },
  "is_default": false
}
```

### Fields

- **name**: Unique name for the profile
- **description**: Human-readable description
- **rules**: Scoring rules (see below)
- **is_default**: Whether this is the default profile

### Rules Structure

#### Event Weights

Map of event types to their numeric weights:

```json
"event_weights": {
  "email_sent": 1.0,
  "email_open": 3.0,
  "meeting": 15.0
}
```

- Positive weights increase scores
- Negative weights decrease scores
- Missing event types default to 0.0

#### Time Decay

Controls how older events are weighted:

```json
"time_decay": {
  "enabled": true,      // Enable/disable decay
  "decay_days": 90,     // Events older than this are decayed
  "decay_factor": 0.5   // Multiplier for old events (0.0-1.0)
}
```

**Example:**
- Event weight: 10.0
- Event age: 100 days
- Decay threshold: 90 days
- Decay factor: 0.5
- **Final weight: 10.0 × 0.5 = 5.0**

## Default Profile

The default profile provides balanced scoring:

```json
{
  "name": "Default",
  "description": "Balanced scoring with standard event weights",
  "rules": {
    "event_weights": {
      "email_sent": 1.0,
      "email_open": 3.0,
      "email_click": 5.0,
      "email_reply": 10.0,
      "email_bounce": -2.0,
      "call": 8.0,
      "meeting": 15.0,
      "message": 5.0,
      "note_added": 3.0,
      "task_completed": 5.0,
      "deal_created": 20.0,
      "deal_stage_change": 15.0,
      "deal_won": 50.0,
      "deal_lost": -10.0,
      "form_submit": 12.0,
      "page_view": 1.0,
      "download": 7.0
    },
    "time_decay": {
      "enabled": true,
      "decay_days": 90,
      "decay_factor": 0.5
    }
  },
  "is_default": true
}
```

## Example Profiles

### Sales-Focused Profile

Emphasizes meetings, calls, and deal activities:

```json
{
  "name": "Sales-Focused",
  "description": "Optimized for sales teams - emphasizes direct contact and deals",
  "rules": {
    "event_weights": {
      "email_sent": 1.0,
      "email_open": 2.0,
      "email_click": 3.0,
      "email_reply": 8.0,
      "call": 15.0,
      "meeting": 30.0,
      "message": 8.0,
      "deal_created": 25.0,
      "deal_stage_change": 20.0,
      "deal_won": 100.0,
      "deal_lost": -5.0
    },
    "time_decay": {
      "enabled": true,
      "decay_days": 60,
      "decay_factor": 0.3
    }
  },
  "is_default": false
}
```

**Characteristics:**
- High weight for meetings (30.0) and calls (15.0)
- Deal progression heavily weighted
- Aggressive decay (60 days, 0.3 factor)
- Email activity less important

**Use Case:** Prioritize contacts with recent sales interactions

### Marketing-Focused Profile

Emphasizes content engagement and email interactions:

```json
{
  "name": "Marketing-Focused",
  "description": "Optimized for marketing teams - emphasizes content and email engagement",
  "rules": {
    "event_weights": {
      "email_sent": 2.0,
      "email_open": 5.0,
      "email_click": 10.0,
      "email_reply": 15.0,
      "call": 5.0,
      "meeting": 10.0,
      "form_submit": 20.0,
      "page_view": 2.0,
      "download": 12.0
    },
    "time_decay": {
      "enabled": true,
      "decay_days": 120,
      "decay_factor": 0.6
    }
  },
  "is_default": false
}
```

**Characteristics:**
- High weight for clicks (10.0) and form submits (20.0)
- Email engagement heavily weighted
- Gentle decay (120 days, 0.6 factor)
- Meetings less critical

**Use Case:** Identify contacts engaging with content

### Customer Success Profile

Tracks ongoing engagement and support interactions:

```json
{
  "name": "Customer-Success",
  "description": "Track customer health and engagement post-sale",
  "rules": {
    "event_weights": {
      "email_sent": 1.0,
      "email_open": 3.0,
      "email_reply": 8.0,
      "call": 10.0,
      "meeting": 15.0,
      "message": 6.0,
      "note_added": 4.0,
      "task_completed": 8.0,
      "deal_stage_change": 5.0,
      "deal_won": 0.0,
      "deal_lost": -50.0
    },
    "time_decay": {
      "enabled": true,
      "decay_days": 45,
      "decay_factor": 0.4
    }
  },
  "is_default": false
}
```

**Characteristics:**
- Balanced communication weights
- Deal loss heavily penalized
- Short decay window (45 days)
- Regular touchpoints important

**Use Case:** Monitor customer health and identify at-risk accounts

### High-Touch Enterprise Profile

For enterprise accounts requiring frequent engagement:

```json
{
  "name": "High-Touch-Enterprise",
  "description": "For strategic enterprise accounts requiring frequent touchpoints",
  "rules": {
    "event_weights": {
      "email_sent": 2.0,
      "email_open": 4.0,
      "email_click": 6.0,
      "email_reply": 12.0,
      "call": 20.0,
      "meeting": 35.0,
      "message": 10.0,
      "note_added": 5.0,
      "task_completed": 8.0,
      "deal_created": 30.0,
      "deal_stage_change": 25.0,
      "deal_won": 150.0
    },
    "time_decay": {
      "enabled": true,
      "decay_days": 30,
      "decay_factor": 0.2
    }
  },
  "is_default": false
}
```

**Characteristics:**
- Very high meeting weight (35.0)
- Aggressive decay (30 days, 0.2 factor)
- All activities weighted higher
- Recent engagement critical

**Use Case:** Track strategic accounts requiring frequent executive attention

### No-Decay Profile

All events weighted equally regardless of age:

```json
{
  "name": "No-Decay",
  "description": "All historical events weighted equally - no time decay",
  "rules": {
    "event_weights": {
      "email_sent": 1.0,
      "email_open": 3.0,
      "meeting": 15.0
    },
    "time_decay": {
      "enabled": false
    }
  },
  "is_default": false
}
```

**Use Case:** Historical analysis, lifetime engagement tracking

## Score Calculation Examples

### Example 1: Contact with Mixed Events

**Events:**
- 5 emails sent (weight: 1.0 each)
- 3 emails opened (weight: 3.0 each)
- 1 meeting (weight: 15.0)
- All within last 30 days (no decay)

**Calculation:**
```
Score = (5 × 1.0) + (3 × 3.0) + (1 × 15.0)
      = 5 + 9 + 15
      = 29.0
```

### Example 2: Contact with Decay

**Events:**
- 2 meetings @ 120 days old (weight: 15.0 each)
- 1 meeting @ 20 days old (weight: 15.0)

**Profile:** decay_days=90, decay_factor=0.5

**Calculation:**
```
Old meetings: 2 × 15.0 × 0.5 = 15.0
Recent meeting: 1 × 15.0 = 15.0
Total = 30.0
```

### Example 3: Deal Lifecycle

**Events:**
- Deal created (weight: 20.0)
- 3 stage changes (weight: 15.0 each)
- Deal won (weight: 50.0)

**Calculation:**
```
Score = 20.0 + (3 × 15.0) + 50.0
      = 20.0 + 45.0 + 50.0
      = 115.0
```

## Creating Profiles via API

```bash
curl -X POST http://localhost:8001/api/v1/profiles \
  -H "Content-Type: application/json" \
  -d @profile.json
```

## Creating Profiles via CLI

Direct database insertion:

```python
from app.core import get_session
from app.repositories import ScoringProfileRepository

db = get_session()
repo = ScoringProfileRepository(db)

profile = repo.create(
    name="Custom Profile",
    description="My custom scoring rules",
    rules={
        "event_weights": {...},
        "time_decay": {...}
    },
    is_default=False
)

db.close()
```

## Best Practices

### 1. Start with Default

Begin with the default profile and adjust based on results.

### 2. Test with Dry Runs

Use dry runs to test profile changes:

```bash
# Recalculate with specific profile without saving
python -m app.cli.main recalc-all --profile-id 2
```

### 3. Monitor Score Distributions

Check average scores after profile changes:

```bash
curl http://localhost:8001/api/v1/stats
```

### 4. Document Custom Profiles

Include clear descriptions of why weights were chosen.

### 5. Version Your Profiles

Keep historical profiles for comparison and rollback.

### 6. A/B Test Profiles

Compare results from different profiles on the same dataset.

## Common Patterns

### Pattern: Penalize Negative Events

```json
"event_weights": {
  "email_bounce": -2.0,
  "deal_lost": -10.0,
  "unsubscribe": -5.0
}
```

### Pattern: Boost Recent Activity

```json
"time_decay": {
  "enabled": true,
  "decay_days": 30,
  "decay_factor": 0.2
}
```

### Pattern: Different Weights by Channel

```json
"event_weights": {
  "email_reply": 10.0,
  "linkedin_message": 8.0,
  "whatsapp_message": 6.0
}
```

### Pattern: Stage-Based Weighting

```json
"event_weights": {
  "deal_stage_change_to_demo": 15.0,
  "deal_stage_change_to_negotiation": 25.0,
  "deal_stage_change_to_contract": 35.0
}
```

## Troubleshooting

### Scores Too High/Low

Adjust event weights proportionally:
- If all scores too high: divide all weights by 2
- If all scores too low: multiply all weights by 2

### No Differentiation

Increase weight variance:
- Make important events much heavier
- Make minor events lighter

### Decay Too Aggressive

Increase `decay_factor` (closer to 1.0) or `decay_days`.

### Negative Scores

Review negative weights - ensure they're intentional.
