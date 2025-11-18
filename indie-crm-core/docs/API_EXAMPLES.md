# API Examples

Complete HTTP request examples for all IndieStack CRM endpoints.

**Base URL**: `http://localhost:8000/api/v1`

## Table of Contents
- [Contacts](#contacts)
- [Companies](#companies)
- [Deals](#deals)
- [Activities](#activities)
- [Pipelines & Stages](#pipelines--stages)
- [Associations](#associations)

---

## Contacts

### List Contacts
```bash
# Get all contacts
curl "http://localhost:8000/api/v1/contacts"

# With pagination
curl "http://localhost:8000/api/v1/contacts?skip=0&limit=50"

# Filter by category
curl "http://localhost:8000/api/v1/contacts?category=buyer"

# Filter by active status
curl "http://localhost:8000/api/v1/contacts?is_active=true"

# Combined filters
curl "http://localhost:8000/api/v1/contacts?category=seller&is_active=true&limit=10"
```

### Get Single Contact
```bash
curl "http://localhost:8000/api/v1/contacts/1"
```

### Create Contact (Seller)
```bash
curl -X POST "http://localhost:8000/api/v1/contacts" \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "Robert",
    "last_name": "Johnson",
    "primary_email": "robert.johnson@business.com",
    "phone": "+1-415-555-0123",
    "linkedin_url": "https://linkedin.com/in/robertjohnson",
    "category": "seller",
    "primary_language": "English",
    "is_active": true,
    "details": {
      "timeline_to_sell": "6-12 months",
      "pain_points": "Looking to retire and transition to advisory role",
      "expectation": "Seeking strategic buyer who will maintain company culture"
    }
  }'
```

### Create Contact (Buyer)
```bash
curl -X POST "http://localhost:8000/api/v1/contacts" \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "Sarah",
    "last_name": "Chen",
    "primary_email": "sarah.chen@investmentfirm.com",
    "phone": "+1-650-555-0199",
    "category": "buyer",
    "details": {
      "industry": "SaaS",
      "budget": 5000000,
      "geographic_preference": "North America",
      "passive_ownership": false,
      "timeline_to_buy": "3-6 months",
      "financial_capacity_verification": "Pre-qualified with $10M credit line",
      "background_experience": "15 years in tech M&A"
    }
  }'
```

### Update Contact
```bash
curl -X PUT "http://localhost:8000/api/v1/contacts/1" \
  -H "Content-Type: application/json" \
  -d '{
    "phone": "+1-415-555-9999",
    "is_active": false,
    "details": {
      "timeline_to_sell": "3-6 months",
      "updated_notes": "Urgency increased due to health reasons"
    }
  }'
```

### Delete Contact
```bash
curl -X DELETE "http://localhost:8000/api/v1/contacts/1"
```

---

## Companies

### List Companies
```bash
# Get all companies
curl "http://localhost:8000/api/v1/companies"

# Filter by industry
curl "http://localhost:8000/api/v1/companies?industry=Technology"

# With pagination
curl "http://localhost:8000/api/v1/companies?skip=10&limit=20"
```

### Search Companies by Name
```bash
# Partial match, case-insensitive
curl "http://localhost:8000/api/v1/companies/search?name=tech"
```

### Get Single Company
```bash
curl "http://localhost:8000/api/v1/companies/5"
```

### Create Company
```bash
curl -X POST "http://localhost:8000/api/v1/companies" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "CloudTech Solutions Inc",
    "location": "San Francisco, CA",
    "website": "https://cloudtechsolutions.com",
    "linkedin_url": "https://linkedin.com/company/cloudtech-solutions",
    "industry": "SaaS",
    "revenue": 12500000,
    "employees": 75,
    "earnings": 2800000,
    "fiscal_year_end": "12-31",
    "founded_year": 2018,
    "recurring_arr": 10000000,
    "details": {
      "growth_rate": "35% YoY",
      "customer_count": 450,
      "churn_rate": "5%",
      "tech_stack": ["React", "Node.js", "PostgreSQL", "AWS"]
    }
  }'
```

### Update Company
```bash
curl -X PUT "http://localhost:8000/api/v1/companies/5" \
  -H "Content-Type: application/json" \
  -d '{
    "revenue": 15000000,
    "employees": 85,
    "details": {
      "growth_rate": "40% YoY",
      "recent_funding": "$5M Series A"
    }
  }'
```

### Delete Company
```bash
curl -X DELETE "http://localhost:8000/api/v1/companies/5"
```

---

## Deals

### List Deals
```bash
# Get all deals
curl "http://localhost:8000/api/v1/deals"

# Filter by pipeline
curl "http://localhost:8000/api/v1/deals?pipeline_id=1"

# Filter by stage
curl "http://localhost:8000/api/v1/deals?stage_id=5"

# Filter by status
curl "http://localhost:8000/api/v1/deals?status=open"

# Filter by pipeline type
curl "http://localhost:8000/api/v1/deals?pipeline_type=buyer"

# Filter by owner
curl "http://localhost:8000/api/v1/deals?owner_id=10"

# Combined filters
curl "http://localhost:8000/api/v1/deals?pipeline_type=seller&status=open&limit=25"
```

### Get Single Deal
```bash
curl "http://localhost:8000/api/v1/deals/3"
```

### Create Deal
```bash
curl -X POST "http://localhost:8000/api/v1/deals" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "CloudTech Solutions Acquisition",
    "pipeline_type": "buyer",
    "pipeline_id": 2,
    "stage_id": 5,
    "amount": 8500000,
    "currency": "USD",
    "expected_close_date": "2025-06-30",
    "owner_id": 10,
    "status": "open",
    "details": {
      "deal_source": "Broker referral",
      "competitive_situation": "2 other interested buyers",
      "key_drivers": ["Strong ARR growth", "Low churn", "Defensible moat"],
      "risks": ["Key person dependency", "Geographic concentration"]
    }
  }'
```

### Update Deal (Move to Next Stage)
```bash
curl -X PUT "http://localhost:8000/api/v1/deals/3" \
  -H "Content-Type: application/json" \
  -d '{
    "stage_id": 6,
    "details": {
      "stage_update_notes": "LOI accepted, moving to due diligence",
      "loi_amount": 8500000
    }
  }'
```

### Update Deal (Mark as Won)
```bash
curl -X PUT "http://localhost:8000/api/v1/deals/3" \
  -H "Content-Type: application/json" \
  -d '{
    "stage_id": 8,
    "status": "won",
    "amount": 8750000,
    "details": {
      "closing_notes": "Deal closed successfully with 3% premium",
      "actual_close_date": "2025-06-28"
    }
  }'
```

### Delete Deal
```bash
curl -X DELETE "http://localhost:8000/api/v1/deals/3"
```

---

## Activities

### List Activities
```bash
# Get all activities
curl "http://localhost:8000/api/v1/activities"

# Filter by type
curl "http://localhost:8000/api/v1/activities?type=call"

# Filter by owner
curl "http://localhost:8000/api/v1/activities?owner_id=10"

# With pagination
curl "http://localhost:8000/api/v1/activities?skip=0&limit=50"
```

### Get Single Activity
```bash
curl "http://localhost:8000/api/v1/activities/15"
```

### Create Activity (Call)
```bash
curl -X POST "http://localhost:8000/api/v1/activities" \
  -H "Content-Type: application/json" \
  -d '{
    "type": "call",
    "subject": "Initial discovery call with CloudTech CEO",
    "content": "Discussed business metrics, growth trajectory, and exit timeline. CEO is motivated to sell within 6 months. Key concerns: employee retention and culture fit.",
    "direction": "outgoing",
    "happened_at": "2025-01-15T14:30:00Z",
    "owner_id": 10,
    "details": {
      "duration_minutes": 45,
      "call_outcome": "Positive - scheduling follow-up",
      "next_steps": ["Send NDA", "Schedule facility tour", "Request financials"]
    }
  }'
```

### Create Activity (Email)
```bash
curl -X POST "http://localhost:8000/api/v1/activities" \
  -H "Content-Type: application/json" \
  -d '{
    "type": "email",
    "subject": "Follow-up: Financial documentation request",
    "content": "Hi Robert,\n\nThank you for the productive call yesterday. As discussed, please find attached our NDA...",
    "direction": "outgoing",
    "happened_at": "2025-01-16T09:15:00Z",
    "owner_id": 10,
    "details": {
      "thread_id": "thread-abc123",
      "message_id": "msg-xyz789",
      "attachments": ["NDA.pdf", "Financial_Template.xlsx"]
    }
  }'
```

### Create Activity (Meeting)
```bash
curl -X POST "http://localhost:8000/api/v1/activities" \
  -H "Content-Type: application/json" \
  -d '{
    "type": "meeting",
    "subject": "On-site facility tour and team introduction",
    "content": "Conducted comprehensive facility tour. Met engineering team, reviewed product roadmap, discussed organizational structure.",
    "direction": "outgoing",
    "happened_at": "2025-01-20T10:00:00Z",
    "owner_id": 10,
    "details": {
      "location": "CloudTech HQ, San Francisco",
      "attendees": ["Robert Johnson (CEO)", "Sarah Chen (Buyer)", "Mike (CTO)", "Lisa (CFO)"],
      "duration_minutes": 180,
      "video_url": null,
      "key_takeaways": ["Strong team culture", "Well-documented processes", "Modern tech stack"]
    }
  }'
```

### Create Activity (Note)
```bash
curl -X POST "http://localhost:8000/api/v1/activities" \
  -H "Content-Type: application/json" \
  -d '{
    "type": "note",
    "subject": "Deal strategy discussion",
    "content": "Internal team discussion on deal approach. Consensus to move forward with LOI at $8.5M. Key negotiation points: earn-out structure, employment agreements for key employees, non-compete terms.",
    "direction": null,
    "happened_at": "2025-01-21T15:00:00Z",
    "owner_id": 10,
    "details": {
      "internal_only": true,
      "participants": ["Sarah Chen", "Investment Committee"]
    }
  }'
```

### Update Activity
```bash
curl -X PUT "http://localhost:8000/api/v1/activities/15" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Updated notes: CEO confirmed 6-month timeline is firm due to personal health reasons.",
    "details": {
      "follow_up_completed": true,
      "outcome": "NDA signed, financials received"
    }
  }'
```

### Delete Activity
```bash
curl -X DELETE "http://localhost:8000/api/v1/activities/15"
```

---

## Pipelines & Stages

### List Pipelines
```bash
# Get all pipelines
curl "http://localhost:8000/api/v1/pipelines"

# Filter by type
curl "http://localhost:8000/api/v1/pipelines?type=seller"

# Filter by active status
curl "http://localhost:8000/api/v1/pipelines?is_active=true"
```

### Get Single Pipeline (with stages)
```bash
curl "http://localhost:8000/api/v1/pipelines/1"
```

### Create Pipeline
```bash
curl -X POST "http://localhost:8000/api/v1/pipelines" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Strategic Partnerships Pipeline",
    "type": "buyer",
    "is_active": true
  }'
```

### Update Pipeline
```bash
curl -X PUT "http://localhost:8000/api/v1/pipelines/1" \
  -H "Content-Type: application/json" \
  -d '{
    "is_active": false
  }'
```

### Delete Pipeline
```bash
curl -X DELETE "http://localhost:8000/api/v1/pipelines/1"
```

### List Stages for Pipeline
```bash
curl "http://localhost:8000/api/v1/pipelines/1/stages"
```

### Create Stage
```bash
curl -X POST "http://localhost:8000/api/v1/pipelines/stages" \
  -H "Content-Type: application/json" \
  -d '{
    "pipeline_id": 1,
    "name": "Qualification",
    "order_index": 1,
    "is_closed_won": false,
    "is_closed_lost": false
  }'
```

### Update Stage
```bash
curl -X PUT "http://localhost:8000/api/v1/pipelines/stages/5" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "LOI Submitted and Under Review",
    "order_index": 5
  }'
```

### Delete Stage
```bash
curl -X DELETE "http://localhost:8000/api/v1/pipelines/stages/5"
```

---

## Associations

Associations link entities together in many-to-many relationships.

### Contact-Company Associations

#### Link Contact to Company
```bash
curl -X POST "http://localhost:8000/api/v1/associations/contact-company" \
  -H "Content-Type: application/json" \
  -d '{
    "contact_id": 1,
    "company_id": 5,
    "role": "CEO & Founder",
    "is_primary": true
  }'
```

#### Get Companies for Contact
```bash
curl "http://localhost:8000/api/v1/associations/contact/1/companies"
```

#### Get Contacts for Company
```bash
curl "http://localhost:8000/api/v1/associations/company/5/contacts"
```

#### Unlink Contact from Company
```bash
curl -X DELETE "http://localhost:8000/api/v1/associations/contact-company/1/5"
```

### Contact-Deal Associations

#### Link Contact to Deal
```bash
curl -X POST "http://localhost:8000/api/v1/associations/contact-deal" \
  -H "Content-Type: application/json" \
  -d '{
    "contact_id": 1,
    "deal_id": 3,
    "role": "Seller / Decision Maker"
  }'
```

#### Get Deals for Contact
```bash
curl "http://localhost:8000/api/v1/associations/contact/1/deals"
```

#### Get Contacts for Deal
```bash
curl "http://localhost:8000/api/v1/associations/deal/3/contacts"
```

#### Unlink Contact from Deal
```bash
curl -X DELETE "http://localhost:8000/api/v1/associations/contact-deal/1/3"
```

### Company-Deal Associations

#### Link Company to Deal
```bash
curl -X POST "http://localhost:8000/api/v1/associations/company-deal" \
  -H "Content-Type: application/json" \
  -d '{
    "company_id": 5,
    "deal_id": 3,
    "role": "Target Company"
  }'
```

#### Get Deals for Company
```bash
curl "http://localhost:8000/api/v1/associations/company/5/deals"
```

#### Get Companies for Deal
```bash
curl "http://localhost:8000/api/v1/associations/deal/3/companies"
```

#### Unlink Company from Deal
```bash
curl -X DELETE "http://localhost:8000/api/v1/associations/company-deal/5/3"
```

### Activity-Contact Associations

#### Link Activity to Contact
```bash
curl -X POST "http://localhost:8000/api/v1/associations/activity-contact" \
  -H "Content-Type: application/json" \
  -d '{
    "activity_id": 15,
    "contact_id": 1
  }'
```

#### Get Contacts for Activity
```bash
curl "http://localhost:8000/api/v1/associations/activity/15/contacts"
```

#### Unlink Activity from Contact
```bash
curl -X DELETE "http://localhost:8000/api/v1/associations/activity-contact/15/1"
```

### Activity-Company Associations

#### Link Activity to Company
```bash
curl -X POST "http://localhost:8000/api/v1/associations/activity-company" \
  -H "Content-Type: application/json" \
  -d '{
    "activity_id": 15,
    "company_id": 5
  }'
```

#### Get Companies for Activity
```bash
curl "http://localhost:8000/api/v1/associations/activity/15/companies"
```

#### Unlink Activity from Company
```bash
curl -X DELETE "http://localhost:8000/api/v1/associations/activity-company/15/5"
```

### Activity-Deal Associations

#### Link Activity to Deal
```bash
curl -X POST "http://localhost:8000/api/v1/associations/activity-deal" \
  -H "Content-Type: application/json" \
  -d '{
    "activity_id": 15,
    "deal_id": 3
  }'
```

#### Get Deals for Activity
```bash
curl "http://localhost:8000/api/v1/associations/activity/15/deals"
```

#### Unlink Activity from Deal
```bash
curl -X DELETE "http://localhost:8000/api/v1/associations/activity-deal/15/3"
```

---

## Complete Workflow Example

Here's a complete example of tracking a deal from initial contact to close:

### 1. Create Seller Contact
```bash
curl -X POST "http://localhost:8000/api/v1/contacts" \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "Robert",
    "last_name": "Johnson",
    "primary_email": "robert@cloudtech.com",
    "category": "seller",
    "details": {"timeline_to_sell": "6 months"}
  }'
# Returns: {"id": 1, ...}
```

### 2. Create Target Company
```bash
curl -X POST "http://localhost:8000/api/v1/companies" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "CloudTech Solutions",
    "industry": "SaaS",
    "revenue": 12500000,
    "employees": 75
  }'
# Returns: {"id": 5, ...}
```

### 3. Link Contact to Company
```bash
curl -X POST "http://localhost:8000/api/v1/associations/contact-company" \
  -H "Content-Type: application/json" \
  -d '{"contact_id": 1, "company_id": 5, "role": "CEO", "is_primary": true}'
```

### 4. Create Deal
```bash
curl -X POST "http://localhost:8000/api/v1/deals" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "CloudTech Acquisition",
    "pipeline_type": "buyer",
    "pipeline_id": 2,
    "stage_id": 5,
    "amount": 8500000,
    "owner_id": 10
  }'
# Returns: {"id": 3, ...}
```

### 5. Link Contact and Company to Deal
```bash
curl -X POST "http://localhost:8000/api/v1/associations/contact-deal" \
  -H "Content-Type: application/json" \
  -d '{"contact_id": 1, "deal_id": 3, "role": "Seller"}'

curl -X POST "http://localhost:8000/api/v1/associations/company-deal" \
  -H "Content-Type: application/json" \
  -d '{"company_id": 5, "deal_id": 3, "role": "Target"}'
```

### 6. Log Discovery Call
```bash
curl -X POST "http://localhost:8000/api/v1/activities" \
  -H "Content-Type: application/json" \
  -d '{
    "type": "call",
    "subject": "Discovery call",
    "content": "Initial discussion of business and exit plans",
    "direction": "outgoing",
    "owner_id": 10,
    "details": {"duration_minutes": 45}
  }'
# Returns: {"id": 15, ...}
```

### 7. Link Activity to Contact, Company, and Deal
```bash
curl -X POST "http://localhost:8000/api/v1/associations/activity-contact" \
  -H "Content-Type: application/json" \
  -d '{"activity_id": 15, "contact_id": 1}'

curl -X POST "http://localhost:8000/api/v1/associations/activity-company" \
  -H "Content-Type: application/json" \
  -d '{"activity_id": 15, "company_id": 5}'

curl -X POST "http://localhost:8000/api/v1/associations/activity-deal" \
  -H "Content-Type: application/json" \
  -d '{"activity_id": 15, "deal_id": 3}'
```

### 8. Move Deal Through Stages
```bash
# Move to Due Diligence
curl -X PUT "http://localhost:8000/api/v1/deals/3" \
  -H "Content-Type: application/json" \
  -d '{"stage_id": 6}'

# Move to Closing
curl -X PUT "http://localhost:8000/api/v1/deals/3" \
  -H "Content-Type: application/json" \
  -d '{"stage_id": 7}'

# Mark as Won
curl -X PUT "http://localhost:8000/api/v1/deals/3" \
  -H "Content-Type: application/json" \
  -d '{"stage_id": 8, "status": "won", "amount": 8750000}'
```

---

## Response Formats

All successful responses return JSON with the created/updated resource:

```json
{
  "id": 1,
  "first_name": "Robert",
  "last_name": "Johnson",
  "primary_email": "robert@cloudtech.com",
  "category": "seller",
  "is_active": true,
  "details": {
    "timeline_to_sell": "6 months"
  },
  "created_at": "2025-01-15T10:30:00Z",
  "updated_at": "2025-01-15T10:30:00Z"
}
```

Error responses include a detail message:

```json
{
  "detail": "Contact with email robert@cloudtech.com already exists"
}
```

## Testing with Python

```python
import requests

BASE_URL = "http://localhost:8000/api/v1"

# Create a contact
response = requests.post(
    f"{BASE_URL}/contacts",
    json={
        "first_name": "Jane",
        "last_name": "Doe",
        "primary_email": "jane@example.com",
        "category": "buyer"
    }
)
contact = response.json()
print(f"Created contact: {contact['id']}")

# Get all open deals
response = requests.get(f"{BASE_URL}/deals", params={"status": "open"})
deals = response.json()
print(f"Found {len(deals)} open deals")
```
