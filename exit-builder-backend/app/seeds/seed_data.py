"""
Seed data for Exit Builder Backend
Populates initial questionnaire, score dimensions, and score rules
"""
import uuid
from sqlalchemy.orm import Session
from app.models import (
    QuestionnaireTemplate,
    Question,
    QuestionOption,
    ScoreDimension,
    ScoreRule,
    ReportTemplate,
)
from app.models.questionnaire import InputType
from app.models.score import MatchType


def seed_report_templates(db: Session):
    """Seed report templates"""
    templates = [
        {
            "code": "QUICK_REPORT",
            "name": "Quick Valuation Report",
            "description": "Basic valuation report with financial analysis",
            "is_active": True,
        },
        {
            "code": "STANDARD_REPORT",
            "name": "Exit Ready MPSP Report",
            "description": "Comprehensive Exit Ready report with scorecard and valuation",
            "is_active": True,
        }
    ]

    for template_data in templates:
        existing = db.query(ReportTemplate).filter_by(code=template_data["code"]).first()
        if not existing:
            template = ReportTemplate(**template_data)
            db.add(template)

    db.commit()
    print("✓ Seeded report templates")


def seed_questionnaire_template(db: Session):
    """Seed Exit Ready Standard questionnaire template"""
    existing = db.query(QuestionnaireTemplate).filter_by(name="Exit Ready Standard").first()
    if existing:
        print("✓ Questionnaire template already exists")
        return existing.id

    template = QuestionnaireTemplate(
        name="Exit Ready Standard",
        description="Exit Ready MPSP - Standard valuation questionnaire",
        version=1,
        is_active=True
    )
    db.add(template)
    db.commit()
    db.refresh(template)

    print(f"✓ Seeded questionnaire template: {template.name}")
    return template.id


def seed_questions(db: Session, template_id: uuid.UUID):
    """Seed questionnaire questions"""

    questions_data = [
        # OWNER DEPENDENCY SECTION
        {
            "section": "Owner Dependency",
            "order_index": 1,
            "code": "Q_OWNER_ROLE",
            "text": "What is your current role in day-to-day operations?",
            "input_type": InputType.SINGLE_CHOICE,
            "is_required": True,
            "help_text": "How involved are you in the daily running of the business?",
            "options": [
                {"value": "FULL_TIME_OPERATIONAL", "label": "Full-time, deeply involved in operations", "order_index": 1},
                {"value": "PART_TIME_STRATEGIC", "label": "Part-time, mostly strategic decisions", "order_index": 2},
                {"value": "OCCASIONAL_OVERSIGHT", "label": "Occasional oversight, team runs operations", "order_index": 3},
                {"value": "FULLY_DELEGATED", "label": "Fully delegated, business runs without me", "order_index": 4},
            ]
        },
        {
            "section": "Owner Dependency",
            "order_index": 2,
            "code": "Q_MANAGEMENT_TEAM",
            "text": "Do you have a management team that can operate without you?",
            "input_type": InputType.YES_NO,
            "is_required": True,
            "help_text": "Can the business continue to operate effectively in your absence?",
            "options": []
        },
        {
            "section": "Owner Dependency",
            "order_index": 3,
            "code": "Q_KEY_RELATIONSHIPS",
            "text": "Are key customer/supplier relationships dependent on you personally?",
            "input_type": InputType.SINGLE_CHOICE,
            "is_required": True,
            "help_text": "Would customers/suppliers stay if you exited?",
            "options": [
                {"value": "HIGHLY_DEPENDENT", "label": "Highly dependent on me personally", "order_index": 1},
                {"value": "MODERATELY_DEPENDENT", "label": "Moderately dependent, but transitional", "order_index": 2},
                {"value": "LOW_DEPENDENCY", "label": "Low dependency, team has relationships", "order_index": 3},
                {"value": "NO_DEPENDENCY", "label": "No dependency, relationships are institutional", "order_index": 4},
            ]
        },

        # CUSTOMER CONCENTRATION SECTION
        {
            "section": "Customer Concentration",
            "order_index": 4,
            "code": "Q_TOP_CUSTOMER_PCT",
            "text": "What percentage of revenue comes from your largest customer?",
            "input_type": InputType.NUMBER,
            "is_required": True,
            "help_text": "Enter a percentage (e.g., 15 for 15%)",
            "options": []
        },
        {
            "section": "Customer Concentration",
            "order_index": 5,
            "code": "Q_TOP_3_CUSTOMERS_PCT",
            "text": "What percentage of revenue comes from your top 3 customers?",
            "input_type": InputType.NUMBER,
            "is_required": True,
            "help_text": "Enter a percentage (e.g., 40 for 40%)",
            "options": []
        },
        {
            "section": "Customer Concentration",
            "order_index": 6,
            "code": "Q_CUSTOMER_CONTRACTS",
            "text": "Do you have long-term contracts with major customers?",
            "input_type": InputType.SINGLE_CHOICE,
            "is_required": True,
            "help_text": "Contracts reduce risk from customer concentration",
            "options": [
                {"value": "NO_CONTRACTS", "label": "No written contracts", "order_index": 1},
                {"value": "SHORT_TERM", "label": "Short-term contracts (<1 year)", "order_index": 2},
                {"value": "MEDIUM_TERM", "label": "Medium-term contracts (1-3 years)", "order_index": 3},
                {"value": "LONG_TERM", "label": "Long-term contracts (3+ years)", "order_index": 4},
            ]
        },

        # SYSTEMS & PROCESSES SECTION
        {
            "section": "Systems & Processes",
            "order_index": 7,
            "code": "Q_DOCUMENTED_PROCESSES",
            "text": "Are your key business processes documented?",
            "input_type": InputType.SINGLE_CHOICE,
            "is_required": True,
            "help_text": "Documentation makes the business transferable",
            "options": [
                {"value": "NO_DOCUMENTATION", "label": "Not documented, all in people's heads", "order_index": 1},
                {"value": "PARTIAL_DOCUMENTATION", "label": "Partially documented", "order_index": 2},
                {"value": "MOSTLY_DOCUMENTED", "label": "Mostly documented", "order_index": 3},
                {"value": "FULLY_DOCUMENTED", "label": "Fully documented with SOPs", "order_index": 4},
            ]
        },
        {
            "section": "Systems & Processes",
            "order_index": 8,
            "code": "Q_TECHNOLOGY_SYSTEMS",
            "text": "How would you rate your business technology and systems?",
            "input_type": InputType.SINGLE_CHOICE,
            "is_required": True,
            "help_text": "Modern systems increase business value",
            "options": [
                {"value": "OUTDATED", "label": "Outdated or manual processes", "order_index": 1},
                {"value": "BASIC", "label": "Basic systems, some automation", "order_index": 2},
                {"value": "MODERN", "label": "Modern systems, well integrated", "order_index": 3},
                {"value": "ADVANCED", "label": "Advanced, cutting-edge technology", "order_index": 4},
            ]
        },
        {
            "section": "Systems & Processes",
            "order_index": 9,
            "code": "Q_CRM_SYSTEM",
            "text": "Do you use a CRM system to manage customer relationships?",
            "input_type": InputType.YES_NO,
            "is_required": True,
            "help_text": "CRM systems demonstrate organized customer management",
            "options": []
        },

        # FINANCIAL QUALITY SECTION
        {
            "section": "Financial Quality",
            "order_index": 10,
            "code": "Q_FINANCIAL_RECORDS",
            "text": "How accurate and current are your financial records?",
            "input_type": InputType.SINGLE_CHOICE,
            "is_required": True,
            "help_text": "Clean financials are essential for valuation",
            "options": [
                {"value": "INFORMAL", "label": "Informal/incomplete records", "order_index": 1},
                {"value": "BASIC_BOOKKEEPING", "label": "Basic bookkeeping, not always current", "order_index": 2},
                {"value": "PROFESSIONAL", "label": "Professional bookkeeping, current", "order_index": 3},
                {"value": "AUDITED", "label": "Professionally audited financials", "order_index": 4},
            ]
        },
        {
            "section": "Financial Quality",
            "order_index": 11,
            "code": "Q_RECURRING_REVENUE_PCT",
            "text": "What percentage of your revenue is recurring/predictable?",
            "input_type": InputType.NUMBER,
            "is_required": True,
            "help_text": "Recurring revenue increases business value (enter percentage)",
            "options": []
        },
        {
            "section": "Financial Quality",
            "order_index": 12,
            "code": "Q_GROSS_MARGIN",
            "text": "What is your approximate gross profit margin?",
            "input_type": InputType.NUMBER,
            "is_required": True,
            "help_text": "Higher margins indicate stronger business model (enter percentage)",
            "options": []
        },

        # GROWTH & MARKET SECTION
        {
            "section": "Growth & Market",
            "order_index": 13,
            "code": "Q_REVENUE_TREND",
            "text": "What has been your revenue trend over the past 3 years?",
            "input_type": InputType.SINGLE_CHOICE,
            "is_required": True,
            "help_text": "Growth trends impact valuation significantly",
            "options": [
                {"value": "DECLINING", "label": "Declining", "order_index": 1},
                {"value": "FLAT", "label": "Flat (±5%)", "order_index": 2},
                {"value": "MODERATE_GROWTH", "label": "Moderate growth (5-15% annually)", "order_index": 3},
                {"value": "STRONG_GROWTH", "label": "Strong growth (>15% annually)", "order_index": 4},
            ]
        },
        {
            "section": "Growth & Market",
            "order_index": 14,
            "code": "Q_MARKET_POSITION",
            "text": "What is your competitive position in your market?",
            "input_type": InputType.SINGLE_CHOICE,
            "is_required": True,
            "help_text": "Market leaders command premium valuations",
            "options": [
                {"value": "FOLLOWER", "label": "Small player in crowded market", "order_index": 1},
                {"value": "ESTABLISHED", "label": "Established player", "order_index": 2},
                {"value": "STRONG_POSITION", "label": "Strong position with clear differentiation", "order_index": 3},
                {"value": "MARKET_LEADER", "label": "Market leader in niche", "order_index": 4},
            ]
        },
        {
            "section": "Growth & Market",
            "order_index": 15,
            "code": "Q_COMPETITIVE_ADVANTAGE",
            "text": "Do you have a clear, defensible competitive advantage?",
            "input_type": InputType.SINGLE_CHOICE,
            "is_required": True,
            "help_text": "Patents, proprietary technology, brand, or unique positioning",
            "options": [
                {"value": "NO_ADVANTAGE", "label": "No clear advantage", "order_index": 1},
                {"value": "WEAK_ADVANTAGE", "label": "Weak or easily replicated advantage", "order_index": 2},
                {"value": "MODERATE_ADVANTAGE", "label": "Moderate, somewhat defensible advantage", "order_index": 3},
                {"value": "STRONG_ADVANTAGE", "label": "Strong, highly defensible advantage", "order_index": 4},
            ]
        },

        # TEAM & CULTURE SECTION
        {
            "section": "Team & Culture",
            "order_index": 16,
            "code": "Q_KEY_EMPLOYEES",
            "text": "How many employees are critical to business operations?",
            "input_type": InputType.SINGLE_CHOICE,
            "is_required": True,
            "help_text": "Lower dependency on specific individuals reduces risk",
            "options": [
                {"value": "OWNER_ONLY", "label": "Just the owner", "order_index": 1},
                {"value": "FEW_CRITICAL", "label": "2-3 critical people", "order_index": 2},
                {"value": "SMALL_TEAM", "label": "Small team (4-10 people)", "order_index": 3},
                {"value": "DISTRIBUTED", "label": "Well-distributed team, no single points of failure", "order_index": 4},
            ]
        },
        {
            "section": "Team & Culture",
            "order_index": 17,
            "code": "Q_EMPLOYEE_RETENTION",
            "text": "What is your average employee tenure?",
            "input_type": InputType.SINGLE_CHOICE,
            "is_required": True,
            "help_text": "High retention indicates stable, healthy culture",
            "options": [
                {"value": "SHORT_TENURE", "label": "Less than 1 year", "order_index": 1},
                {"value": "MODERATE_TENURE", "label": "1-3 years", "order_index": 2},
                {"value": "GOOD_TENURE", "label": "3-5 years", "order_index": 3},
                {"value": "EXCELLENT_TENURE", "label": "5+ years", "order_index": 4},
            ]
        },

        # LEGAL & COMPLIANCE SECTION
        {
            "section": "Legal & Compliance",
            "order_index": 18,
            "code": "Q_LEGAL_STRUCTURE",
            "text": "Is your legal structure appropriate for a sale?",
            "input_type": InputType.SINGLE_CHOICE,
            "is_required": True,
            "help_text": "Clean legal structure facilitates transactions",
            "options": [
                {"value": "INFORMAL", "label": "Sole proprietorship or informal", "order_index": 1},
                {"value": "BASIC_LLC", "label": "Basic LLC/corporation", "order_index": 2},
                {"value": "CLEAN_STRUCTURE", "label": "Clean corporate structure", "order_index": 3},
                {"value": "OPTIMIZED", "label": "Fully optimized for sale", "order_index": 4},
            ]
        },
        {
            "section": "Legal & Compliance",
            "order_index": 19,
            "code": "Q_IP_PROTECTION",
            "text": "Have you protected your intellectual property?",
            "input_type": InputType.SINGLE_CHOICE,
            "is_required": True,
            "help_text": "Trademarks, patents, copyrights, trade secrets",
            "options": [
                {"value": "NO_PROTECTION", "label": "No formal IP protection", "order_index": 1},
                {"value": "MINIMAL_PROTECTION", "label": "Minimal protection", "order_index": 2},
                {"value": "GOOD_PROTECTION", "label": "Good protection of key IP", "order_index": 3},
                {"value": "COMPREHENSIVE", "label": "Comprehensive IP protection", "order_index": 4},
            ]
        },
        {
            "section": "Legal & Compliance",
            "order_index": 20,
            "code": "Q_COMPLIANCE_ISSUES",
            "text": "Are you fully compliant with all regulatory requirements?",
            "input_type": InputType.YES_NO,
            "is_required": True,
            "help_text": "Compliance issues can derail sales",
            "options": []
        },
    ]

    question_ids = {}

    for q_data in questions_data:
        options_data = q_data.pop("options")

        existing = db.query(Question).filter_by(code=q_data["code"]).first()
        if existing:
            question_ids[q_data["code"]] = existing.id
            continue

        question = Question(
            questionnaire_template_id=template_id,
            **q_data
        )
        db.add(question)
        db.commit()
        db.refresh(question)

        question_ids[q_data["code"]] = question.id

        # Add options
        for opt_data in options_data:
            option = QuestionOption(
                question_id=question.id,
                **opt_data
            )
            db.add(option)

        db.commit()

    print(f"✓ Seeded {len(questions_data)} questions")
    return question_ids


def seed_score_dimensions(db: Session):
    """Seed score dimensions"""

    dimensions_data = [
        {
            "code": "OWNER_DEP",
            "name": "Owner Dependency",
            "description": "Measures how dependent the business is on the owner",
            "weight": 0.25
        },
        {
            "code": "CUSTOMER_CONC",
            "name": "Customer Concentration",
            "description": "Measures revenue concentration and customer risk",
            "weight": 0.20
        },
        {
            "code": "SYSTEMS",
            "name": "Systems & Processes",
            "description": "Measures system maturity and operational efficiency",
            "weight": 0.20
        },
        {
            "code": "FIN_QUALITY",
            "name": "Financial Quality",
            "description": "Measures financial strength and predictability",
            "weight": 0.20
        },
        {
            "code": "GROWTH",
            "name": "Growth & Market",
            "description": "Measures growth trajectory and market position",
            "weight": 0.15
        },
    ]

    dimension_ids = {}

    for dim_data in dimensions_data:
        existing = db.query(ScoreDimension).filter_by(code=dim_data["code"]).first()
        if existing:
            dimension_ids[dim_data["code"]] = existing.id
            continue

        dimension = ScoreDimension(**dim_data)
        db.add(dimension)
        db.commit()
        db.refresh(dimension)

        dimension_ids[dim_data["code"]] = dimension.id

    print(f"✓ Seeded {len(dimensions_data)} score dimensions")
    return dimension_ids


def seed_score_rules(db: Session, question_ids: dict, dimension_ids: dict):
    """Seed score rules"""

    # Helper to get IDs
    def q(code): return question_ids.get(code)
    def d(code): return dimension_ids.get(code)

    rules_data = [
        # OWNER DEPENDENCY RULES
        {"dimension_id": d("OWNER_DEP"), "question_id": q("Q_OWNER_ROLE"), "match_type": MatchType.OPTION_VALUE, "match_value": "FULL_TIME_OPERATIONAL", "score_delta": 0, "notes": "High owner dependency"},
        {"dimension_id": d("OWNER_DEP"), "question_id": q("Q_OWNER_ROLE"), "match_type": MatchType.OPTION_VALUE, "match_value": "PART_TIME_STRATEGIC", "score_delta": 5, "notes": "Moderate owner dependency"},
        {"dimension_id": d("OWNER_DEP"), "question_id": q("Q_OWNER_ROLE"), "match_type": MatchType.OPTION_VALUE, "match_value": "OCCASIONAL_OVERSIGHT", "score_delta": 10, "notes": "Low owner dependency"},
        {"dimension_id": d("OWNER_DEP"), "question_id": q("Q_OWNER_ROLE"), "match_type": MatchType.OPTION_VALUE, "match_value": "FULLY_DELEGATED", "score_delta": 15, "notes": "Minimal owner dependency"},

        {"dimension_id": d("OWNER_DEP"), "question_id": q("Q_MANAGEMENT_TEAM"), "match_type": MatchType.YES_NO, "match_value": "YES", "score_delta": 10, "notes": "Strong management team"},
        {"dimension_id": d("OWNER_DEP"), "question_id": q("Q_MANAGEMENT_TEAM"), "match_type": MatchType.YES_NO, "match_value": "NO", "score_delta": 0, "notes": "No management team"},

        {"dimension_id": d("OWNER_DEP"), "question_id": q("Q_KEY_RELATIONSHIPS"), "match_type": MatchType.OPTION_VALUE, "match_value": "HIGHLY_DEPENDENT", "score_delta": 0, "notes": "High relationship dependency"},
        {"dimension_id": d("OWNER_DEP"), "question_id": q("Q_KEY_RELATIONSHIPS"), "match_type": MatchType.OPTION_VALUE, "match_value": "MODERATELY_DEPENDENT", "score_delta": 3, "notes": "Moderate relationship dependency"},
        {"dimension_id": d("OWNER_DEP"), "question_id": q("Q_KEY_RELATIONSHIPS"), "match_type": MatchType.OPTION_VALUE, "match_value": "LOW_DEPENDENCY", "score_delta": 7, "notes": "Low relationship dependency"},
        {"dimension_id": d("OWNER_DEP"), "question_id": q("Q_KEY_RELATIONSHIPS"), "match_type": MatchType.OPTION_VALUE, "match_value": "NO_DEPENDENCY", "score_delta": 10, "notes": "No relationship dependency"},

        # CUSTOMER CONCENTRATION RULES
        {"dimension_id": d("CUSTOMER_CONC"), "question_id": q("Q_TOP_CUSTOMER_PCT"), "match_type": MatchType.NUMERIC_RANGE, "match_value": "<10", "score_delta": 15, "notes": "Low concentration"},
        {"dimension_id": d("CUSTOMER_CONC"), "question_id": q("Q_TOP_CUSTOMER_PCT"), "match_type": MatchType.NUMERIC_RANGE, "match_value": "10-25", "score_delta": 10, "notes": "Moderate concentration"},
        {"dimension_id": d("CUSTOMER_CONC"), "question_id": q("Q_TOP_CUSTOMER_PCT"), "match_type": MatchType.NUMERIC_RANGE, "match_value": "25-50", "score_delta": 5, "notes": "High concentration"},
        {"dimension_id": d("CUSTOMER_CONC"), "question_id": q("Q_TOP_CUSTOMER_PCT"), "match_type": MatchType.NUMERIC_RANGE, "match_value": ">50", "score_delta": 0, "notes": "Very high concentration"},

        {"dimension_id": d("CUSTOMER_CONC"), "question_id": q("Q_TOP_3_CUSTOMERS_PCT"), "match_type": MatchType.NUMERIC_RANGE, "match_value": "<25", "score_delta": 10, "notes": "Well diversified"},
        {"dimension_id": d("CUSTOMER_CONC"), "question_id": q("Q_TOP_3_CUSTOMERS_PCT"), "match_type": MatchType.NUMERIC_RANGE, "match_value": "25-50", "score_delta": 5, "notes": "Moderate diversification"},
        {"dimension_id": d("CUSTOMER_CONC"), "question_id": q("Q_TOP_3_CUSTOMERS_PCT"), "match_type": MatchType.NUMERIC_RANGE, "match_value": ">50", "score_delta": 0, "notes": "Poor diversification"},

        {"dimension_id": d("CUSTOMER_CONC"), "question_id": q("Q_CUSTOMER_CONTRACTS"), "match_type": MatchType.OPTION_VALUE, "match_value": "NO_CONTRACTS", "score_delta": 0, "notes": "No contract protection"},
        {"dimension_id": d("CUSTOMER_CONC"), "question_id": q("Q_CUSTOMER_CONTRACTS"), "match_type": MatchType.OPTION_VALUE, "match_value": "SHORT_TERM", "score_delta": 3, "notes": "Short contract protection"},
        {"dimension_id": d("CUSTOMER_CONC"), "question_id": q("Q_CUSTOMER_CONTRACTS"), "match_type": MatchType.OPTION_VALUE, "match_value": "MEDIUM_TERM", "score_delta": 7, "notes": "Medium contract protection"},
        {"dimension_id": d("CUSTOMER_CONC"), "question_id": q("Q_CUSTOMER_CONTRACTS"), "match_type": MatchType.OPTION_VALUE, "match_value": "LONG_TERM", "score_delta": 10, "notes": "Strong contract protection"},

        # SYSTEMS & PROCESSES RULES
        {"dimension_id": d("SYSTEMS"), "question_id": q("Q_DOCUMENTED_PROCESSES"), "match_type": MatchType.OPTION_VALUE, "match_value": "NO_DOCUMENTATION", "score_delta": 0, "notes": "No process documentation"},
        {"dimension_id": d("SYSTEMS"), "question_id": q("Q_DOCUMENTED_PROCESSES"), "match_type": MatchType.OPTION_VALUE, "match_value": "PARTIAL_DOCUMENTATION", "score_delta": 5, "notes": "Partial documentation"},
        {"dimension_id": d("SYSTEMS"), "question_id": q("Q_DOCUMENTED_PROCESSES"), "match_type": MatchType.OPTION_VALUE, "match_value": "MOSTLY_DOCUMENTED", "score_delta": 10, "notes": "Good documentation"},
        {"dimension_id": d("SYSTEMS"), "question_id": q("Q_DOCUMENTED_PROCESSES"), "match_type": MatchType.OPTION_VALUE, "match_value": "FULLY_DOCUMENTED", "score_delta": 15, "notes": "Excellent documentation"},

        {"dimension_id": d("SYSTEMS"), "question_id": q("Q_TECHNOLOGY_SYSTEMS"), "match_type": MatchType.OPTION_VALUE, "match_value": "OUTDATED", "score_delta": 0, "notes": "Outdated technology"},
        {"dimension_id": d("SYSTEMS"), "question_id": q("Q_TECHNOLOGY_SYSTEMS"), "match_type": MatchType.OPTION_VALUE, "match_value": "BASIC", "score_delta": 5, "notes": "Basic technology"},
        {"dimension_id": d("SYSTEMS"), "question_id": q("Q_TECHNOLOGY_SYSTEMS"), "match_type": MatchType.OPTION_VALUE, "match_value": "MODERN", "score_delta": 10, "notes": "Modern technology"},
        {"dimension_id": d("SYSTEMS"), "question_id": q("Q_TECHNOLOGY_SYSTEMS"), "match_type": MatchType.OPTION_VALUE, "match_value": "ADVANCED", "score_delta": 15, "notes": "Advanced technology"},

        {"dimension_id": d("SYSTEMS"), "question_id": q("Q_CRM_SYSTEM"), "match_type": MatchType.YES_NO, "match_value": "YES", "score_delta": 5, "notes": "Has CRM system"},
        {"dimension_id": d("SYSTEMS"), "question_id": q("Q_CRM_SYSTEM"), "match_type": MatchType.YES_NO, "match_value": "NO", "score_delta": 0, "notes": "No CRM system"},

        # FINANCIAL QUALITY RULES
        {"dimension_id": d("FIN_QUALITY"), "question_id": q("Q_FINANCIAL_RECORDS"), "match_type": MatchType.OPTION_VALUE, "match_value": "INFORMAL", "score_delta": 0, "notes": "Informal records"},
        {"dimension_id": d("FIN_QUALITY"), "question_id": q("Q_FINANCIAL_RECORDS"), "match_type": MatchType.OPTION_VALUE, "match_value": "BASIC_BOOKKEEPING", "score_delta": 5, "notes": "Basic bookkeeping"},
        {"dimension_id": d("FIN_QUALITY"), "question_id": q("Q_FINANCIAL_RECORDS"), "match_type": MatchType.OPTION_VALUE, "match_value": "PROFESSIONAL", "score_delta": 10, "notes": "Professional records"},
        {"dimension_id": d("FIN_QUALITY"), "question_id": q("Q_FINANCIAL_RECORDS"), "match_type": MatchType.OPTION_VALUE, "match_value": "AUDITED", "score_delta": 15, "notes": "Audited financials"},

        {"dimension_id": d("FIN_QUALITY"), "question_id": q("Q_RECURRING_REVENUE_PCT"), "match_type": MatchType.NUMERIC_RANGE, "match_value": ">70", "score_delta": 15, "notes": "High recurring revenue"},
        {"dimension_id": d("FIN_QUALITY"), "question_id": q("Q_RECURRING_REVENUE_PCT"), "match_type": MatchType.NUMERIC_RANGE, "match_value": "50-70", "score_delta": 10, "notes": "Good recurring revenue"},
        {"dimension_id": d("FIN_QUALITY"), "question_id": q("Q_RECURRING_REVENUE_PCT"), "match_type": MatchType.NUMERIC_RANGE, "match_value": "25-50", "score_delta": 5, "notes": "Moderate recurring revenue"},
        {"dimension_id": d("FIN_QUALITY"), "question_id": q("Q_RECURRING_REVENUE_PCT"), "match_type": MatchType.NUMERIC_RANGE, "match_value": "<25", "score_delta": 0, "notes": "Low recurring revenue"},

        {"dimension_id": d("FIN_QUALITY"), "question_id": q("Q_GROSS_MARGIN"), "match_type": MatchType.NUMERIC_RANGE, "match_value": ">60", "score_delta": 10, "notes": "Excellent margins"},
        {"dimension_id": d("FIN_QUALITY"), "question_id": q("Q_GROSS_MARGIN"), "match_type": MatchType.NUMERIC_RANGE, "match_value": "40-60", "score_delta": 7, "notes": "Good margins"},
        {"dimension_id": d("FIN_QUALITY"), "question_id": q("Q_GROSS_MARGIN"), "match_type": MatchType.NUMERIC_RANGE, "match_value": "20-40", "score_delta": 3, "notes": "Average margins"},
        {"dimension_id": d("FIN_QUALITY"), "question_id": q("Q_GROSS_MARGIN"), "match_type": MatchType.NUMERIC_RANGE, "match_value": "<20", "score_delta": 0, "notes": "Low margins"},

        # GROWTH & MARKET RULES
        {"dimension_id": d("GROWTH"), "question_id": q("Q_REVENUE_TREND"), "match_type": MatchType.OPTION_VALUE, "match_value": "DECLINING", "score_delta": 0, "notes": "Declining revenue"},
        {"dimension_id": d("GROWTH"), "question_id": q("Q_REVENUE_TREND"), "match_type": MatchType.OPTION_VALUE, "match_value": "FLAT", "score_delta": 5, "notes": "Flat revenue"},
        {"dimension_id": d("GROWTH"), "question_id": q("Q_REVENUE_TREND"), "match_type": MatchType.OPTION_VALUE, "match_value": "MODERATE_GROWTH", "score_delta": 10, "notes": "Moderate growth"},
        {"dimension_id": d("GROWTH"), "question_id": q("Q_REVENUE_TREND"), "match_type": MatchType.OPTION_VALUE, "match_value": "STRONG_GROWTH", "score_delta": 15, "notes": "Strong growth"},

        {"dimension_id": d("GROWTH"), "question_id": q("Q_MARKET_POSITION"), "match_type": MatchType.OPTION_VALUE, "match_value": "FOLLOWER", "score_delta": 0, "notes": "Market follower"},
        {"dimension_id": d("GROWTH"), "question_id": q("Q_MARKET_POSITION"), "match_type": MatchType.OPTION_VALUE, "match_value": "ESTABLISHED", "score_delta": 5, "notes": "Established player"},
        {"dimension_id": d("GROWTH"), "question_id": q("Q_MARKET_POSITION"), "match_type": MatchType.OPTION_VALUE, "match_value": "STRONG_POSITION", "score_delta": 10, "notes": "Strong position"},
        {"dimension_id": d("GROWTH"), "question_id": q("Q_MARKET_POSITION"), "match_type": MatchType.OPTION_VALUE, "match_value": "MARKET_LEADER", "score_delta": 15, "notes": "Market leader"},

        {"dimension_id": d("GROWTH"), "question_id": q("Q_COMPETITIVE_ADVANTAGE"), "match_type": MatchType.OPTION_VALUE, "match_value": "NO_ADVANTAGE", "score_delta": 0, "notes": "No competitive advantage"},
        {"dimension_id": d("GROWTH"), "question_id": q("Q_COMPETITIVE_ADVANTAGE"), "match_type": MatchType.OPTION_VALUE, "match_value": "WEAK_ADVANTAGE", "score_delta": 3, "notes": "Weak advantage"},
        {"dimension_id": d("GROWTH"), "question_id": q("Q_COMPETITIVE_ADVANTAGE"), "match_type": MatchType.OPTION_VALUE, "match_value": "MODERATE_ADVANTAGE", "score_delta": 7, "notes": "Moderate advantage"},
        {"dimension_id": d("GROWTH"), "question_id": q("Q_COMPETITIVE_ADVANTAGE"), "match_type": MatchType.OPTION_VALUE, "match_value": "STRONG_ADVANTAGE", "score_delta": 10, "notes": "Strong advantage"},
    ]

    for rule_data in rules_data:
        if rule_data["dimension_id"] is None or rule_data["question_id"] is None:
            continue

        existing = db.query(ScoreRule).filter_by(
            dimension_id=rule_data["dimension_id"],
            question_id=rule_data["question_id"],
            match_value=rule_data["match_value"]
        ).first()

        if existing:
            continue

        rule = ScoreRule(**rule_data)
        db.add(rule)

    db.commit()
    print(f"✓ Seeded {len(rules_data)} score rules")


def run_seeds(db: Session):
    """Run all seed functions"""
    print("\n=== Seeding Exit Builder Database ===\n")

    seed_report_templates(db)
    template_id = seed_questionnaire_template(db)
    question_ids = seed_questions(db, template_id)
    dimension_ids = seed_score_dimensions(db)
    seed_score_rules(db, question_ids, dimension_ids)

    print("\n=== Seeding Complete! ===\n")


if __name__ == "__main__":
    from app.database import SessionLocal
    db = SessionLocal()
    try:
        run_seeds(db)
    finally:
        db.close()
