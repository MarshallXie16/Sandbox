# Database Schema & ERD

## Entity Relationship Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         IndieStack CRM Data Model                            │
└─────────────────────────────────────────────────────────────────────────────┘

┌──────────────────────┐         ┌──────────────────────┐
│     CONTACTS         │         │     COMPANIES        │
├──────────────────────┤         ├──────────────────────┤
│ id (PK)              │         │ id (PK)              │
│ first_name           │         │ name                 │
│ last_name            │         │ location             │
│ primary_email (UQ)   │         │ website              │
│ secondary_email      │         │ linkedin_url         │
│ phone                │         │ industry             │
│ linkedin_url         │         │ revenue              │
│ whatsapp             │         │ employees            │
│ wechat               │         │ earnings             │
│ primary_language     │         │ fiscal_year_end      │
│ category             │         │ founded_year         │
│ is_active            │         │ recurring_arr        │
│ details (JSONB)      │         │ details (JSONB)      │
│ created_at           │         │ created_at           │
│ updated_at           │         │ updated_at           │
└──────────────────────┘         └──────────────────────┘
         │                                  │
         │                                  │
         │    ┌──────────────────────┐     │
         └────│  CONTACT_COMPANIES   │─────┘
              ├──────────────────────┤
              │ id (PK)              │
              │ contact_id (FK)      │
              │ company_id (FK)      │
              │ role                 │
              │ is_primary           │
              └──────────────────────┘


┌──────────────────────┐         ┌──────────────────────┐
│   DEAL_PIPELINES     │         │    DEAL_STAGES       │
├──────────────────────┤         ├──────────────────────┤
│ id (PK)              │◄────┐   │ id (PK)              │
│ name                 │     └───│ pipeline_id (FK)     │
│ type (seller/buyer)  │         │ name                 │
│ is_active            │         │ order_index          │
└──────────────────────┘         │ is_closed_won        │
         △                        │ is_closed_lost       │
         │                        └──────────────────────┘
         │                                 △
         │                                 │
         │         ┌──────────────────────┐│
         │         │       DEALS          ││
         │         ├──────────────────────┤│
         └─────────│ id (PK)              ││
                   │ name                 ││
                   │ pipeline_type        ││
                   │ pipeline_id (FK)     ││
                   │ stage_id (FK) ───────┘
                   │ amount               │
                   │ currency             │
                   │ expected_close_date  │
                   │ owner_id             │
                   │ status               │
                   │ details (JSONB)      │
                   │ created_at           │
                   │ updated_at           │
                   └──────────────────────┘
                            │
         ┌──────────────────┼──────────────────┐
         │                  │                  │
         ▼                  ▼                  ▼
┌──────────────────┐ ┌──────────────┐ ┌──────────────┐
│  CONTACT_DEALS   │ │ COMPANY_DEALS│ │ACTIVITY_DEALS│
├──────────────────┤ ├──────────────┤ ├──────────────┤
│ id (PK)          │ │ id (PK)      │ │ id (PK)      │
│ contact_id (FK)  │ │ company_id   │ │ activity_id  │
│ deal_id (FK)     │ │ deal_id (FK) │ │ deal_id (FK) │
│ role             │ │ role         │ └──────────────┘
└──────────────────┘ └──────────────┘


┌──────────────────────┐
│     ACTIVITIES       │
├──────────────────────┤
│ id (PK)              │
│ type                 │
│ subject              │
│ content              │
│ direction            │
│ happened_at          │
│ owner_id             │
│ details (JSONB)      │
│ created_at           │
│ updated_at           │
└──────────────────────┘
         │
         ├─────────────┬─────────────┐
         ▼             ▼             ▼
┌──────────────┐ ┌──────────────┐ (to deals above)
│ACTIVITY_     │ │ACTIVITY_     │
│CONTACTS      │ │COMPANIES     │
├──────────────┤ ├──────────────┤
│ id (PK)      │ │ id (PK)      │
│ activity_id  │ │ activity_id  │
│ contact_id   │ │ company_id   │
└──────────────┘ └──────────────┘
```

## Table Details

### contacts
Primary entity for individuals in the CRM.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY | Auto-incrementing ID |
| first_name | VARCHAR(100) | NOT NULL | First name |
| last_name | VARCHAR(100) | NOT NULL | Last name |
| primary_email | VARCHAR(255) | UNIQUE, NOT NULL | Primary email address |
| secondary_email | VARCHAR(255) | NULL | Secondary email |
| phone | VARCHAR(50) | NULL | Phone number |
| linkedin_url | VARCHAR(500) | NULL | LinkedIn profile URL |
| whatsapp | VARCHAR(50) | NULL | WhatsApp number |
| wechat | VARCHAR(100) | NULL | WeChat ID |
| primary_language | VARCHAR(50) | DEFAULT 'English' | Preferred language |
| category | ENUM | NOT NULL | seller/buyer/banker/lawyer/accountant/investor/other |
| is_active | BOOLEAN | DEFAULT TRUE | Active status |
| details | JSONB | DEFAULT '{}' | Extensible custom fields |
| created_at | TIMESTAMP | AUTO | Creation timestamp |
| updated_at | TIMESTAMP | AUTO | Last update timestamp |

**Indexes**: id (PK), primary_email (unique), category, is_active

**Category-Specific Details Fields**:
- Sellers: `timeline_to_sell`, `pain_points`, `expectation`
- Buyers: `industry`, `budget`, `geographic_preference`, `passive_ownership`, `timeline_to_buy`, `financial_capacity_verification`, `background_experience`

### companies
Organization entities.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY | Auto-incrementing ID |
| name | VARCHAR(255) | NOT NULL | Company name |
| location | VARCHAR(255) | NULL | Physical location |
| website | VARCHAR(500) | NULL | Website URL |
| linkedin_url | VARCHAR(500) | NULL | LinkedIn company page |
| industry | VARCHAR(100) | NULL | Industry classification |
| revenue | FLOAT | NULL | Annual revenue |
| employees | INTEGER | NULL | Employee count |
| earnings | FLOAT | NULL | EBITDA or net earnings |
| fiscal_year_end | VARCHAR(10) | NULL | Fiscal year end (MM-DD) |
| founded_year | INTEGER | NULL | Year founded |
| recurring_arr | FLOAT | NULL | Annual Recurring Revenue |
| details | JSONB | DEFAULT '{}' | Extensible custom fields |
| created_at | TIMESTAMP | AUTO | Creation timestamp |
| updated_at | TIMESTAMP | AUTO | Last update timestamp |

**Indexes**: id (PK), name, industry

### deals
Sales opportunities.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY | Auto-incrementing ID |
| name | VARCHAR(255) | NOT NULL | Deal name/title |
| pipeline_type | ENUM | NOT NULL | seller/buyer |
| pipeline_id | INTEGER | FK → deal_pipelines | Pipeline reference |
| stage_id | INTEGER | FK → deal_stages | Current stage |
| amount | FLOAT | NULL | Deal value |
| currency | VARCHAR(3) | DEFAULT 'USD' | Currency code (ISO 4217) |
| expected_close_date | DATE | NULL | Expected closing date |
| owner_id | INTEGER | NULL | Owner user ID (future FK) |
| status | ENUM | DEFAULT 'open' | open/won/lost |
| details | JSONB | DEFAULT '{}' | Extensible custom fields |
| created_at | TIMESTAMP | AUTO | Creation timestamp |
| updated_at | TIMESTAMP | AUTO | Last update timestamp |

**Indexes**: id (PK), pipeline_id, stage_id, status, pipeline_type

### activities
Interaction logs.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY | Auto-incrementing ID |
| type | ENUM | NOT NULL | email/call/meeting/linkedin/whatsapp/wechat/note |
| subject | VARCHAR(500) | NULL | Activity subject/title |
| content | TEXT | NULL | Activity content/notes |
| direction | ENUM | NULL | incoming/outgoing |
| happened_at | TIMESTAMP | NOT NULL | When activity occurred |
| owner_id | INTEGER | NULL | Owner user ID (future FK) |
| details | JSONB | DEFAULT '{}' | Extensible custom fields |
| created_at | TIMESTAMP | AUTO | Creation timestamp |
| updated_at | TIMESTAMP | AUTO | Last update timestamp |

**Indexes**: id (PK), type, happened_at

**Common Details Fields**:
- Email: `thread_id`, `message_id`, `cc`, `bcc`
- Call: `duration_minutes`, `recording_url`
- Meeting: `location`, `attendees`, `video_url`

### deal_pipelines
Pipeline definitions (stored in DB, not hard-coded).

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY | Auto-incrementing ID |
| name | VARCHAR(100) | UNIQUE, NOT NULL | Pipeline name |
| type | ENUM | NOT NULL | seller/buyer |
| is_active | BOOLEAN | DEFAULT TRUE | Active status |

**Default Pipelines**:
1. **Seller Pipeline** (type: seller)
2. **Buyer Pipeline** (type: buyer)

### deal_stages
Stage definitions within pipelines.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY | Auto-incrementing ID |
| pipeline_id | INTEGER | FK → deal_pipelines | Parent pipeline |
| name | VARCHAR(100) | NOT NULL | Stage name |
| order_index | INTEGER | NOT NULL | Order in pipeline (lower = earlier) |
| is_closed_won | BOOLEAN | DEFAULT FALSE | Marks as successful close |
| is_closed_lost | BOOLEAN | DEFAULT FALSE | Marks as failed close |

**Default Seller Pipeline Stages**:
1. Exit Ready Engagement (order: 1)
2. Facilitator Engagement (order: 2)
3. Broker Engagement (order: 3)
4. Marketing (order: 4)
5. LOI Acceptance (order: 5)
6. Due Diligence (order: 6)
7. Closing (order: 7)
8. Won (order: 8, is_closed_won: true)
9. Lost (order: 9, is_closed_lost: true)

**Default Buyer Pipeline Stages**:
1. Buyer Access Agreement (order: 1)
2. Finder Agreement (order: 2)
3. Broker Engagement (order: 3)
4. Marketing (order: 4)
5. LOI Acceptance (order: 5)
6. Due Diligence (order: 6)
7. Closing (order: 7)
8. Won (order: 8, is_closed_won: true)
9. Lost (order: 9, is_closed_lost: true)

## Association Tables

### contact_companies
Links contacts to companies.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY | Auto-incrementing ID |
| contact_id | INTEGER | FK → contacts (CASCADE) | Contact reference |
| company_id | INTEGER | FK → companies (CASCADE) | Company reference |
| role | VARCHAR(100) | NULL | Contact's role (e.g., "CEO") |
| is_primary | BOOLEAN | DEFAULT FALSE | Is this contact's primary company |

**Unique Constraint**: (contact_id, company_id)

### contact_deals
Links contacts to deals.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY | Auto-incrementing ID |
| contact_id | INTEGER | FK → contacts (CASCADE) | Contact reference |
| deal_id | INTEGER | FK → deals (CASCADE) | Deal reference |
| role | VARCHAR(100) | NULL | Contact's role in deal (e.g., "Decision Maker") |

**Unique Constraint**: (contact_id, deal_id)

### company_deals
Links companies to deals.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY | Auto-incrementing ID |
| company_id | INTEGER | FK → companies (CASCADE) | Company reference |
| deal_id | INTEGER | FK → deals (CASCADE) | Deal reference |
| role | VARCHAR(100) | NULL | Company's role in deal (e.g., "Seller") |

**Unique Constraint**: (company_id, deal_id)

### activity_contacts
Links activities to contacts.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY | Auto-incrementing ID |
| activity_id | INTEGER | FK → activities (CASCADE) | Activity reference |
| contact_id | INTEGER | FK → contacts (CASCADE) | Contact reference |

**Unique Constraint**: (activity_id, contact_id)

### activity_companies
Links activities to companies.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY | Auto-incrementing ID |
| activity_id | INTEGER | FK → activities (CASCADE) | Activity reference |
| company_id | INTEGER | FK → companies (CASCADE) | Company reference |

**Unique Constraint**: (activity_id, company_id)

### activity_deals
Links activities to deals.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY | Auto-incrementing ID |
| activity_id | INTEGER | FK → activities (CASCADE) | Activity reference |
| deal_id | INTEGER | FK → deals (CASCADE) | Deal reference |

**Unique Constraint**: (activity_id, deal_id)

## Key Design Decisions

### 1. JSONB Details Field
All main entities include a `details` JSONB column for:
- Category-specific attributes (seller vs. buyer contacts)
- Integration metadata (external system IDs)
- Future custom fields without schema changes
- Flexible querying with PostgreSQL JSON operators

### 2. Pipelines in Database
Unlike many CRMs that hard-code deal stages, this system stores pipelines and stages in the database:
- Allows runtime customization via API
- Supports multiple pipelines per type
- Easy to add new pipeline types in future
- Stages can be reordered, renamed, or archived

### 3. Association Tables with Metadata
Association tables include metadata fields like `role`:
- Contact-Company: "CEO", "CFO", "Board Member"
- Contact-Deal: "Decision Maker", "Influencer", "Champion"
- Company-Deal: "Seller", "Buyer", "Advisor"

This mirrors HubSpot's association model.

### 4. Cascade Deletes
All foreign keys in association tables use `CASCADE` delete:
- Deleting a contact removes all its associations
- Deleting a company removes all its associations
- Prevents orphaned association records

### 5. Nullable owner_id
The `owner_id` fields on deals and activities are nullable integers:
- Allows future integration with user management system
- Can be used immediately with external user IDs
- No FK constraint yet (for flexibility)

## Query Examples

### Find all contacts at a specific company
```sql
SELECT c.* FROM contacts c
JOIN contact_companies cc ON c.id = cc.contact_id
WHERE cc.company_id = 123;
```

### Find all activities for a deal
```sql
SELECT a.* FROM activities a
JOIN activity_deals ad ON a.id = ad.activity_id
WHERE ad.deal_id = 456
ORDER BY a.happened_at DESC;
```

### Find buyer contacts in a specific industry (custom field)
```sql
SELECT * FROM contacts
WHERE category = 'buyer'
  AND details->>'industry' = 'Technology';
```

### Get all deals in "Due Diligence" stage for seller pipeline
```sql
SELECT d.* FROM deals d
JOIN deal_stages s ON d.stage_id = s.id
WHERE s.name = 'Due Diligence'
  AND d.pipeline_type = 'seller';
```

### Count contacts by category
```sql
SELECT category, COUNT(*) as count
FROM contacts
WHERE is_active = true
GROUP BY category;
```
