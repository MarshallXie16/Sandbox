"""
Seed data script - populates initial reference data

Run this after migrations to populate:
- Valuation methods
- Report templates
- Sample industry multiples
"""
import uuid
from sqlalchemy.orm import Session

from app.core.db import SessionLocal, engine
from app.models import ValuationMethod, ReportTemplate, IndustryMultiple


def seed_valuation_methods(db: Session):
    """Seed valuation methods"""
    methods = [
        {
            "code": "SDE_MULTIPLE",
            "name": "SDE Multiple Method",
            "description": "Valuation based on Seller's Discretionary Earnings multiples",
            "is_active": True
        },
        {
            "code": "EBITDA_MULTIPLE",
            "name": "EBITDA Multiple Method",
            "description": "Valuation based on EBITDA multiples",
            "is_active": True
        }
    ]

    for method_data in methods:
        existing = db.query(ValuationMethod).filter_by(code=method_data["code"]).first()
        if not existing:
            method = ValuationMethod(**method_data)
            db.add(method)
            print(f"✓ Created valuation method: {method_data['code']}")
        else:
            print(f"- Valuation method already exists: {method_data['code']}")

    db.commit()


def seed_report_templates(db: Session):
    """Seed report templates"""
    templates = [
        {
            "code": "QUICK_SUMMARY",
            "name": "Quick Valuation Summary",
            "description": "Simple one-page valuation summary for quick assessments",
            "version": 1,
            "is_active": True
        }
    ]

    for template_data in templates:
        existing = db.query(ReportTemplate).filter_by(code=template_data["code"]).first()
        if not existing:
            template = ReportTemplate(**template_data)
            db.add(template)
            print(f"✓ Created report template: {template_data['code']}")
        else:
            print(f"- Report template already exists: {template_data['code']}")

    db.commit()


def seed_industry_multiples(db: Session):
    """Seed sample industry multiples"""
    multiples = [
        # HVAC Services (238220)
        {
            "industry_code": "238220",
            "metric_type": "SDE",
            "size_min_revenue": 0,
            "size_max_revenue": 2000000,
            "multiple_low": 2.8,
            "multiple_mid": 3.2,
            "multiple_high": 3.6,
            "source": "BizBuySell Market Data 2024",
            "effective_date": "2024-01-01"
        },
        {
            "industry_code": "238220",
            "metric_type": "EBITDA",
            "size_min_revenue": 0,
            "size_max_revenue": 2000000,
            "multiple_low": 4.5,
            "multiple_mid": 5.0,
            "multiple_high": 5.5,
            "source": "BizBuySell Market Data 2024",
            "effective_date": "2024-01-01"
        },
        # Restaurants (722511)
        {
            "industry_code": "722511",
            "metric_type": "SDE",
            "size_min_revenue": 0,
            "size_max_revenue": 1000000,
            "multiple_low": 1.8,
            "multiple_mid": 2.2,
            "multiple_high": 2.6,
            "source": "Restaurant Industry Benchmarks 2024",
            "effective_date": "2024-01-01"
        },
        {
            "industry_code": "722511",
            "metric_type": "EBITDA",
            "size_min_revenue": 0,
            "size_max_revenue": 1000000,
            "multiple_low": 3.0,
            "multiple_mid": 3.5,
            "multiple_high": 4.0,
            "source": "Restaurant Industry Benchmarks 2024",
            "effective_date": "2024-01-01"
        },
        # Professional Services (541611 - Management Consulting)
        {
            "industry_code": "541611",
            "metric_type": "SDE",
            "size_min_revenue": 0,
            "size_max_revenue": 5000000,
            "multiple_low": 2.5,
            "multiple_mid": 3.0,
            "multiple_high": 3.5,
            "source": "Professional Services Market Data 2024",
            "effective_date": "2024-01-01"
        },
        {
            "industry_code": "541611",
            "metric_type": "EBITDA",
            "size_min_revenue": 0,
            "size_max_revenue": 5000000,
            "multiple_low": 4.0,
            "multiple_mid": 5.0,
            "multiple_high": 6.0,
            "source": "Professional Services Market Data 2024",
            "effective_date": "2024-01-01"
        },
        # Retail - General (445110)
        {
            "industry_code": "445110",
            "metric_type": "SDE",
            "size_min_revenue": 0,
            "size_max_revenue": 3000000,
            "multiple_low": 2.0,
            "multiple_mid": 2.5,
            "multiple_high": 3.0,
            "source": "Retail Industry Data 2024",
            "effective_date": "2024-01-01"
        },
        {
            "industry_code": "445110",
            "metric_type": "EBITDA",
            "size_min_revenue": 0,
            "size_max_revenue": 3000000,
            "multiple_low": 3.5,
            "multiple_mid": 4.0,
            "multiple_high": 4.5,
            "source": "Retail Industry Data 2024",
            "effective_date": "2024-01-01"
        }
    ]

    for multiple_data in multiples:
        existing = db.query(IndustryMultiple).filter_by(
            industry_code=multiple_data["industry_code"],
            metric_type=multiple_data["metric_type"]
        ).first()

        if not existing:
            multiple = IndustryMultiple(**multiple_data)
            db.add(multiple)
            print(f"✓ Created industry multiple: {multiple_data['industry_code']} ({multiple_data['metric_type']})")
        else:
            print(f"- Industry multiple already exists: {multiple_data['industry_code']} ({multiple_data['metric_type']})")

    db.commit()


def main():
    """Run all seed operations"""
    print("\n=== Seeding Database ===\n")

    db = SessionLocal()
    try:
        print("1. Seeding Valuation Methods...")
        seed_valuation_methods(db)

        print("\n2. Seeding Report Templates...")
        seed_report_templates(db)

        print("\n3. Seeding Industry Multiples...")
        seed_industry_multiples(db)

        print("\n=== Seeding Complete ===\n")
    except Exception as e:
        print(f"\n✗ Error during seeding: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    main()
