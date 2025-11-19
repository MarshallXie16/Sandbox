# Standard Valuation Flow - Technical Documentation

## Overview

The **Standard Valuation Flow** is the core of Capital Link's **Exit Ready MPSP** (Market Positioned for Sale Program) - a $3,000 premium product that provides comprehensive business exit readiness assessment and valuation.

This document details the technical implementation of the Standard Flow.

## Architecture

The Standard Flow builds on top of the Quick Valuation Flow:

```
Quick Valuation (Baseline)
    ↓
Questionnaire (20 questions)
    ↓
Scorecard Computation (5 dimensions)
    ↓
Valuation Adjustment (0.80x - 1.10x)
    ↓
Standard Valuation Report
```

## Data Model

### Questionnaire System

#### questionnaire_templates
Defines questionnaire versions (e.g., "Exit Ready Standard v1")

```sql
- id: UUID (PK)
- name: STRING
- description: TEXT
- version: INTEGER
- is_active: BOOLEAN
```

#### questions
Individual questions within a questionnaire

```sql
- id: UUID (PK)
- questionnaire_template_id: UUID (FK)
- section: STRING (e.g., "Owner Dependency")
- order_index: INTEGER
- code: STRING UNIQUE (e.g., "Q_OWNER_ROLE")
- text: TEXT (question text)
- input_type: ENUM (single_choice, multi_choice, number, text, yes_no)
- is_required: BOOLEAN
- help_text: TEXT
```

**Input Types:**
- `single_choice` - Radio button selection
- `multi_choice` - Multiple checkbox selections
- `number` - Numeric input (percentages, counts)
- `text` - Free text input
- `yes_no` - Boolean yes/no choice

#### question_options
Answer options for choice-based questions

```sql
- id: UUID (PK)
- question_id: UUID (FK)
- value: STRING (internal code, e.g., "FULLY_DELEGATED")
- label: STRING (user-facing text)
- order_index: INTEGER
```

### Answer Storage

#### answers
User responses to questionnaire questions

```sql
- id: UUID (PK)
- project_id: UUID (FK)
- question_id: UUID (FK)
- value_text: TEXT (for text questions)
- value_numeric: NUMERIC (for number questions)
- selected_option_values: JSONB (for choice questions, e.g., ["HIGH", "MEDIUM"])
- created_at: TIMESTAMP
- updated_at: TIMESTAMP
```

**Storage Strategy:**
- Text questions → `value_text`
- Number questions → `value_numeric`
- Single choice → `selected_option_values: ["VALUE"]`
- Multi choice → `selected_option_values: ["VAL1", "VAL2"]`
- Yes/No → `selected_option_values: ["YES"]` or `["NO"]`

### Scoring System

#### score_dimensions
The five core dimensions that impact business transferability

```sql
- id: UUID (PK)
- code: STRING UNIQUE (e.g., "OWNER_DEP")
- name: STRING
- description: TEXT
- weight: NUMERIC (0.10 - 0.30, sum = 1.00)
```

**Default Dimensions:**

| Code | Name | Weight | Description |
|------|------|--------|-------------|
| OWNER_DEP | Owner Dependency | 0.25 | How dependent is the business on owner |
| CUSTOMER_CONC | Customer Concentration | 0.20 | Revenue concentration risk |
| SYSTEMS | Systems & Processes | 0.20 | Operational maturity |
| FIN_QUALITY | Financial Quality | 0.20 | Financial strength & predictability |
| GROWTH | Growth & Market | 0.15 | Growth trajectory & market position |

#### score_rules
Maps question responses to score deltas

```sql
- id: UUID (PK)
- dimension_id: UUID (FK)
- question_id: UUID (FK)
- match_type: ENUM (option_value, numeric_range, yes_no, text_contains)
- match_value: STRING (pattern to match)
- score_delta: INTEGER (points to add/subtract)
- notes: TEXT
```

**Match Types:**

1. **option_value**: Matches selected option
   - Example: `match_value: "FULLY_DELEGATED"` → `+15 points`

2. **numeric_range**: Matches numeric ranges
   - `"<10"` - Less than 10
   - `"10-25"` - Between 10 and 25 (inclusive)
   - `">50"` - Greater than 50

3. **yes_no**: Matches yes/no answers
   - `match_value: "YES"` → `+10 points`
   - `match_value: "NO"` → `0 points`

4. **text_contains**: Substring matching in text answers
   - `match_value: "documented"` → matches if answer contains "documented"

#### score_results
Overall scorecard result for a project

```sql
- id: UUID (PK)
- project_id: UUID (FK)
- total_score: INTEGER (0-100)
- rating: STRING (A, B, C, D)
- valuation_adjustment_factor: NUMERIC (0.80 - 1.10)
- created_at: TIMESTAMP
```

**Rating System:**

| Score Range | Rating | Adjustment | Meaning |
|-------------|--------|-----------|---------|
| 80-100 | A | 1.10x | Highly exit-ready, premium valuation |
| 65-79 | B | 1.00x | Exit-ready, market valuation |
| 50-64 | C | 0.90x | Moderate improvements needed |
| 0-49 | D | 0.80x | Significant work needed |

#### score_dimension_results
Individual dimension scores within a scorecard

```sql
- id: UUID (PK)
- score_result_id: UUID (FK)
- dimension_id: UUID (FK)
- score: INTEGER (dimension-specific score)
- comment: TEXT (auto-generated commentary)
```

## Score Engine Logic

### Algorithm

```python
def compute_scorecard(project_id):
    1. Load all answers for project

    2. For each dimension:
        a. Get all score_rules for dimension
        b. For each rule:
            - Get answer for rule's question
            - Check if answer matches rule (based on match_type)
            - If match: add score_delta to dimension score
        c. Sum all matched deltas → dimension_score

    3. Calculate weighted total:
        total_score = Σ(dimension_score × dimension.weight)

    4. Normalize to 0-100 scale:
        # Assuming max dimension score ≈ 35 points
        max_possible = 35 × 1.00 = 35 (weighted)
        normalized_score = (total_score / max_possible) × 100

    5. Assign rating:
        if score >= 80: rating = 'A', adjustment = 1.10
        elif score >= 65: rating = 'B', adjustment = 1.00
        elif score >= 50: rating = 'C', adjustment = 0.90
        else: rating = 'D', adjustment = 0.80

    6. Create score_result and score_dimension_results

    7. Return ScoreResult
```

### Example Scoring

**Question:** "What is your current role in day-to-day operations?"

**Rules:**
```
OWNER_DEP dimension:
- "FULL_TIME_OPERATIONAL" → +0 points (high dependency, bad)
- "PART_TIME_STRATEGIC" → +5 points
- "OCCASIONAL_OVERSIGHT" → +10 points
- "FULLY_DELEGATED" → +15 points (low dependency, good)
```

If user selects **"FULLY_DELEGATED"**:
- Owner Dependency dimension gets +15 points
- Contributes: 15 × 0.25 (weight) = 3.75 to weighted total

## Standard Valuation Logic

### Process

```python
def run_standard_valuation(project_id):
    1. Get or create Quick Valuation (baseline)
        - Returns: value_low, value_mid, value_high

    2. Load score_result
        - If missing → raise error "Run compute_scorecard first"

    3. Get adjustment_factor from score_result
        - Rating A → 1.10
        - Rating B → 1.00
        - Rating C → 0.90
        - Rating D → 0.80

    4. Apply adjustment:
        adjusted_low = baseline_low × adjustment_factor
        adjusted_mid = baseline_mid × adjustment_factor
        adjusted_high = baseline_high × adjustment_factor

    5. Update valuation_summary with adjusted values

    6. Return both baseline and adjusted valuations
```

### Example Calculation

**Baseline Valuation (Quick):**
- Low: $8,000,000
- Mid: $10,000,000
- High: $12,000,000

**Scorecard Result:**
- Score: 82/100
- Rating: A
- Adjustment: 1.10x

**Adjusted Valuation:**
- Low: $8,000,000 × 1.10 = $8,800,000
- Mid: $10,000,000 × 1.10 = $11,000,000
- High: $12,000,000 × 1.10 = $13,200,000

**Impact:** The business's strong exit readiness adds $1M to the mid-point valuation.

## Questionnaire Design

### Sections

1. **Owner Dependency (3 questions)**
   - Owner's operational role
   - Management team independence
   - Key relationship dependency

2. **Customer Concentration (3 questions)**
   - Top customer % of revenue
   - Top 3 customers % of revenue
   - Contract terms

3. **Systems & Processes (3 questions)**
   - Process documentation
   - Technology systems quality
   - CRM usage

4. **Financial Quality (3 questions)**
   - Financial record quality
   - Recurring revenue %
   - Gross margin %

5. **Growth & Market (3 questions)**
   - Revenue trend
   - Market position
   - Competitive advantage

6. **Team & Culture (2 questions)**
   - Key employee count
   - Employee retention

7. **Legal & Compliance (3 questions)**
   - Legal structure
   - IP protection
   - Compliance status

**Total:** 20 questions

### Question Example

```python
{
    "code": "Q_OWNER_ROLE",
    "section": "Owner Dependency",
    "text": "What is your current role in day-to-day operations?",
    "input_type": "single_choice",
    "is_required": True,
    "help_text": "How involved are you in the daily running of the business?",
    "options": [
        {
            "value": "FULL_TIME_OPERATIONAL",
            "label": "Full-time, deeply involved in operations"
        },
        {
            "value": "PART_TIME_STRATEGIC",
            "label": "Part-time, mostly strategic decisions"
        },
        {
            "value": "OCCASIONAL_OVERSIGHT",
            "label": "Occasional oversight, team runs operations"
        },
        {
            "value": "FULLY_DELEGATED",
            "label": "Fully delegated, business runs without me"
        }
    ]
}
```

## Report Generation

### Standard Report Structure

```markdown
# Exit Ready MPSP - Standard Valuation Report

## Executive Summary
- Exit Readiness Score
- Adjusted Valuation Range
- Key Highlights

## Business Overview
- Company name, industry, description
- Project information

## Financial Summary
- Current financials
- 3-year trend (if available)
- Key metrics (margins, etc.)

## Exit Readiness Scorecard
### Overall Score: XX/100 (Rating: X)

### Dimension Scores
| Dimension | Score | Weight | Assessment |
|-----------|-------|--------|------------|
| ... | ... | ... | ... |

### Strengths
- Top performing dimensions

### Areas for Improvement
- Weak dimensions with recommendations

## Valuation Results
- Baseline valuation
- Adjustment factor explanation
- Adjusted valuation range

## Recommendations
- Prioritized action items based on weak dimensions
- Next steps

## Disclaimer
- Limitations
- Professional advice recommendation
```

### Report Generation Logic

```python
def generate_standard_report_markdown(project_id):
    1. Load project details
    2. Load valuation_summary (adjusted values)
    3. Load score_result and dimension_results
    4. Load financial_inputs

    5. Build report sections:
        - Executive Summary (score, rating, valuation)
        - Business Overview (project details)
        - Financial Summary (from financial_inputs)
        - Scorecard (scores, strengths, weaknesses)
        - Valuation (baseline vs adjusted)
        - Recommendations (based on weak dimensions)
        - Disclaimer

    6. Return Markdown string

    7. Save to reports table
```

## API Endpoints

### Standard Flow Endpoints

```
POST /api/v1/standard/projects
→ Create Standard project

POST /api/v1/standard/projects/{id}/answers
→ Submit questionnaire answers

GET /api/v1/standard/projects/{id}/answers
→ Retrieve all answers

POST /api/v1/standard/projects/{id}/score
→ Compute scorecard

POST /api/v1/standard/projects/{id}/valuation
→ Run Standard Valuation

POST /api/v1/standard/projects/{id}/report
→ Generate Standard Report

GET /api/v1/standard/projects/{id}
→ Get project details
```

## End-to-End Flow Example

### 1. Create Project

```bash
POST /api/v1/standard/projects
{
  "name": "TechCo Inc",
  "industry": "saas",
  "financial_inputs": [{
    "year": 0,
    "revenue": 2000000,
    "ebitda": 500000
  }]
}
→ Returns: { "id": "uuid", ... }
```

### 2. Submit Answers

```bash
POST /api/v1/standard/projects/{id}/answers
{
  "answers": [
    {
      "question_code": "Q_OWNER_ROLE",
      "selected_option_values": ["FULLY_DELEGATED"]
    },
    {
      "question_code": "Q_TOP_CUSTOMER_PCT",
      "value_numeric": 8
    },
    ...
  ]
}
→ Returns: { "answers_saved": 20 }
```

### 3. Compute Score

```bash
POST /api/v1/standard/projects/{id}/score
→ Returns: {
  "total_score": 82,
  "rating": "A",
  "adjustment_factor": 1.10,
  "dimensions": [...]
}
```

### 4. Run Valuation

```bash
POST /api/v1/standard/projects/{id}/valuation
→ Returns: {
  "baseline_valuation": {
    "value_mid": 10000000
  },
  "adjusted_valuation": {
    "value_mid": 11000000
  },
  "score": { "rating": "A", "adjustment_factor": 1.10 }
}
```

### 5. Generate Report

```bash
POST /api/v1/standard/projects/{id}/report
→ Returns: {
  "report_id": "uuid",
  "content": "# Exit Ready MPSP Report\n\n...",
  "format": "markdown"
}
```

## Extensibility

### Adding New Questions

1. Add question to seed data (`app/seeds/seed_data.py`)
2. Create corresponding score_rules
3. Run seed script
4. Question automatically appears in questionnaire

### Adding New Dimensions

1. Add dimension to `score_dimensions` table
2. Ensure weights sum to 1.00
3. Create score_rules mapping questions to new dimension
4. Update report generation if needed

### Adjusting Scoring

- Modify `score_delta` values in score_rules
- Adjust dimension weights
- Change rating thresholds in `score_engine.py`

## Performance Considerations

- **Caching**: Consider caching questionnaire templates and rules
- **Indexing**: Ensure indexes on foreign keys, question codes
- **Batch Processing**: Scorecard computation can be optimized for multiple projects
- **Database Queries**: Use eager loading for relationships to minimize N+1 queries

## Security Considerations

- **Input Validation**: All API inputs validated via Pydantic schemas
- **SQL Injection**: Protected by SQLAlchemy ORM
- **Authentication**: Not implemented (add JWT/OAuth as needed)
- **Authorization**: No project ownership checks (implement as needed)
- **Data Privacy**: Contains sensitive business information - secure accordingly

## Testing

Comprehensive test suite in `tests/test_standard_flow.py`:

- Project creation
- Answer submission and retrieval
- Scorecard computation
- Standard valuation
- Report generation
- End-to-end flow

Run: `pytest tests/test_standard_flow.py -v`

## Future Enhancements

1. **Conditional Questions**: Show/hide questions based on previous answers
2. **Multi-language Support**: Internationalization of questionnaire
3. **Historical Tracking**: Track scorecard improvements over time
4. **Benchmarking**: Compare scores against industry averages
5. **Action Plans**: Automated improvement recommendations
6. **PDF Reports**: Generate PDF versions of reports
7. **Email Delivery**: Send reports via email
8. **Dashboard**: Visualize scorecard with charts

---

**Standard Flow = Quick Flow + Qualitative Assessment**

The power of the Standard Flow is combining quantitative financial analysis with qualitative business readiness metrics to provide a holistic, actionable valuation.
