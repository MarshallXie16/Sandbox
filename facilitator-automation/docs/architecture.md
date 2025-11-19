# Facilitator Automation - Architecture

## System Overview

Facilitator Automation implements Phase 2 of the Capital Link workflow: managing facilitator engagements, tracking introduced buyers, and calculating facilitator fees.

### Legal & Business Context

**Role**: Facilitator/Finder (NOT Broker/Agent)
- No fiduciary duty to seller
- No agency representation
- Coordination and record-keeping only
- Fee structure: $5k offer fee + 5% success fee with credit

**"Introduced Buyer" Principle**:
Success fees are ONLY calculated when a deal closes with a buyer that has been explicitly introduced through this system. The `facilitator_buyer_intros` table is the source of truth.

## Domain Model

### Core Entities

#### 1. Facilitator Engagement
Represents the Phase 2 relationship between Capital Link and a seller/listing.

**Key attributes**:
- `engagement_code`: Human-readable ID (e.g., FAC-2025-0007)
- `seller_contact_id`, `company_id`, `listing_id`: Links to CRM
- `status`: Engagement lifecycle state
- `offer_fee_fixed`, `success_fee_rate`: Commercial terms
- `start_date`, `end_date`, `tail_end_date`: Timeline

**States**:
```
draft → active → (shortlisting/outreach/offers/under_agreement) →
(closed_success/closed_no_deal/terminated)
```

#### 2. Introduced Buyer
**SOURCE OF TRUTH** for success fee eligibility.

**Key attributes**:
- `engagement_id`: Parent engagement
- `buyer_contact_id`: CRM contact ID
- `introduced_at`: Introduction timestamp
- `status`: Buyer lifecycle (invited → NDA → teaser → info → offer)

**Critical invariant**: A closing can ONLY reference a buyer with an entry in this table.

#### 3. Offer
Tracks non-binding offers from introduced buyers.

**Key attributes**:
- `buyer_intro_id`: Must reference an introduced buyer
- `headline_price`: Offer amount
- `offer_fee_amount`: Fixed fee due (default $5k)
- `offer_fee_invoiced`, `offer_fee_paid`: Payment tracking

#### 4. Closing
Records final deal closure and calculates success fees.

**Key attributes**:
- `buyer_intro_id`: REQUIRED - the introduced buyer who closed
- `final_price`: Transaction price
- `success_fee_gross_amount`: final_price × success_fee_rate
- `offer_fee_credit_amount`: Sum of paid offer fees (capped at gross)
- `success_fee_net_amount`: gross - credit

#### 5. Event (Audit Trail)
Immutable log of all significant actions for compliance.

**Event types**: engagement_created, buyer_introduced, offer_received, closing_recorded, etc.

## Architecture Layers

### 1. Data Layer (Repository Pattern)
- **BaseRepository**: Generic CRUD operations
- **Specialized Repositories**: Engagement, BuyerIntro, Offer, Closing, Event
- Abstracts database operations from business logic

### 2. Business Logic Layer (Services)

#### FeeCalculatorService
Implements fee calculation logic:
```python
success_fee_gross = final_price × success_fee_rate
offer_fee_credit = min(offer_fees_paid, success_fee_gross)
success_fee_net = success_fee_gross - offer_fee_credit
```

#### WorkflowService
Manages engagement state machine:
- Validates state transitions
- Enforces workflow rules
- Maps actions to status changes

#### EngagementService
- Create/activate engagements
- Manage engagement lifecycle
- Status transitions with validation

#### BuyerIntroService
- Introduce buyers (creates Introduced Buyer record)
- Track buyer lifecycle
- Validate buyer belongs to engagement

#### OfferService
- Record offers
- Track offer fees
- Link offers to introduced buyers

#### ClosingService
- Record closings
- Call FeeCalculatorService for fee calculation
- Validate buyer is introduced
- Update engagement to closed_success

### 3. Integration Layer

#### MatchingEngineClient
- Suggests candidate buyers for listings
- Does NOT auto-create Introduced Buyers
- Stub mode for testing

#### EmailEngineClient
- Sends introduction emails
- NDA requests
- Offer notifications
- Stub mode for testing

#### CRMClient
- Retrieves contact/company/listing information
- Falls back to stubs if not configured

### 4. API Layer (FastAPI)
RESTful endpoints under `/api/v1/facilitator`:
- `/engagements` - CRUD and lifecycle
- `/engagements/{id}/buyers` - Introduce and manage buyers
- `/engagements/{id}/offers` - Record and manage offers
- `/engagements/{id}/closings` - Record closings with fee calculation

**Security**: API key authentication via `X-API-Key` header

### 5. CLI Layer (Typer)
Operator-friendly commands:
- `facilitator engagements` - Manage engagements
- `facilitator buyers` - Introduce and track buyers
- `facilitator offers` - Record offers
- `facilitator closings` - Record closings and view fees

## State Machine

### Engagement States

```
┌─────────┐
│  DRAFT  │
└────┬────┘
     │ activate()
     ▼
┌─────────┐     ┌──────────────┐
│ ACTIVE  │────▶│ SHORTLISTING │
└────┬────┘     └──────┬───────┘
     │                 │
     │                 ▼
     │         ┌──────────────────────┐
     ├────────▶│ OUTREACH_IN_PROGRESS │
     │         └──────────┬───────────┘
     │                    │
     │                    ▼
     │         ┌───────────────────┐
     ├────────▶│ OFFERS_IN_PLAY    │
     │         └─────────┬─────────┘
     │                   │
     │                   ▼
     │         ┌──────────────────┐
     └────────▶│ UNDER_AGREEMENT  │
               └─────────┬────────┘
                         │
        ┌────────────────┼────────────────┐
        │                │                │
        ▼                ▼                ▼
┌───────────────┐ ┌─────────────┐ ┌────────────┐
│CLOSED_SUCCESS │ │CLOSED_NO_DEAL│ │ TERMINATED │
└───────────────┘ └─────────────┘ └────────────┘
     (terminal)       (terminal)      (terminal)
```

### Buyer Intro States

```
INVITED → NDA_PENDING → NDA_SIGNED → TEASER_SENT →
INFO_ACCESS → OFFER_MADE

                    ↓
         (INACTIVE/NOT_INTERESTED/DROPPED)
```

## Database Schema

### Tables

1. **facilitator_engagements**
   - Primary engagement tracking
   - Commercial terms
   - Lifecycle status

2. **facilitator_buyer_intros**
   - Introduced buyer records
   - Source of truth for success fee eligibility

3. **facilitator_offers**
   - Offer tracking
   - Offer fee management

4. **facilitator_closings**
   - Final deal closures
   - Success fee calculation results

5. **facilitator_events**
   - Audit trail
   - Compliance logging

### Key Relationships

```
Engagement (1) ──< (N) BuyerIntro
Engagement (1) ──< (N) Offer
Engagement (1) ──< (0..1) Closing

BuyerIntro (1) ──< (N) Offer
BuyerIntro (1) ──< (0..1) Closing
```

## Fee Calculation Design

### Principles

1. **Offer Fee**: Fixed amount (default $5k) when buyer makes offer
2. **Success Fee**: Percentage (default 5%) of final price
3. **Credit**: Offer fees already paid reduce success fee
4. **Cap**: Credit cannot exceed gross success fee

### Implementation

```python
class FeeCalculatorService:
    @staticmethod
    def calculate_success_fee(
        final_price: Decimal,
        success_fee_rate: Decimal,
        offer_fees_paid: Decimal
    ) -> FeeCalculation:
        gross = final_price * success_fee_rate
        credit = min(offer_fees_paid, gross)
        net = gross - credit
        return FeeCalculation(...)
```

### Example Scenarios

**Scenario 1: Normal case**
- Final price: $2M
- Rate: 5%
- Offer fees paid: $5k
- Result: Gross $100k, Credit $5k, Net $95k

**Scenario 2: Multiple offers**
- Final price: $2M
- Rate: 5%
- Offer fees paid: $15k (3 offers × $5k)
- Result: Gross $100k, Credit $15k, Net $85k

**Scenario 3: Low-value deal**
- Final price: $50k
- Rate: 5%
- Offer fees paid: $5k
- Result: Gross $2.5k, Credit $2.5k (capped), Net $0

## Security & Compliance

### API Security
- API key authentication (header-based)
- No keys configured = dev mode only
- Rate limiting recommended (not implemented)

### Audit Trail
Every significant action logged in `facilitator_events`:
- Who did what, when
- Old/new values for state changes
- Structured payload for analysis

### Data Integrity
- Foreign key constraints
- Status transition validation
- Introduced Buyer requirement for closings

## Scalability Considerations

### Current Design
- Single PostgreSQL database
- Async I/O throughout (SQLAlchemy async + FastAPI)
- Suitable for 100s of engagements/day

### Future Scaling
- Add caching layer (Redis) for CRM lookups
- Separate read replicas for reporting
- Event sourcing for audit trail
- Queue system for email sending

## Deployment

### Requirements
- Python 3.10+
- PostgreSQL 12+
- 512MB RAM minimum (1GB recommended)

### Environment
- Development: Single process with --reload
- Production: Multiple workers with Uvicorn + Gunicorn

### Monitoring
- Health endpoint: `/api/v1/health`
- Structured logging (JSON format recommended for production)
- Database connection pool monitoring

---

This architecture ensures compliance, auditability, and clear separation of concerns while maintaining the legal distinction as a facilitator (not broker) service.
