"""
Comprehensive tests for Standard Valuation Flow
"""
import pytest
from app.seeds.seed_data import run_seeds


class TestStandardFlow:
    """Test suite for Standard Valuation Flow"""

    @pytest.fixture(autouse=True)
    def setup(self, db):
        """Setup test data"""
        # Seed database with questionnaire and scoring rules
        run_seeds(db)

    def test_create_standard_project(self, client):
        """Test creating a Standard project"""
        payload = {
            "name": "Test Business Inc",
            "industry": "saas",
            "description": "A test SaaS business",
            "financial_inputs": [
                {
                    "year": 0,
                    "revenue": 500000,
                    "net_profit": 100000,
                    "ebitda": 150000,
                    "total_assets": 300000,
                    "total_liabilities": 100000
                }
            ]
        }

        response = client.post("/api/v1/standard/projects", json=payload)
        assert response.status_code == 201

        data = response.json()
        assert data["name"] == "Test Business Inc"
        assert data["project_type"] == "STANDARD"
        assert data["industry"] == "saas"
        assert "id" in data

        return data["id"]

    def test_submit_answers(self, client):
        """Test submitting questionnaire answers"""
        # Create project first
        project_response = client.post("/api/v1/standard/projects", json={
            "name": "Test Business",
            "industry": "saas",
            "financial_inputs": [
                {"year": 0, "revenue": 500000, "ebitda": 150000}
            ]
        })
        project_id = project_response.json()["id"]

        # Submit answers
        answers_payload = {
            "answers": [
                {
                    "question_code": "Q_OWNER_ROLE",
                    "selected_option_values": ["FULLY_DELEGATED"]
                },
                {
                    "question_code": "Q_MANAGEMENT_TEAM",
                    "selected_option_values": ["YES"]
                },
                {
                    "question_code": "Q_TOP_CUSTOMER_PCT",
                    "value_numeric": 8
                },
                {
                    "question_code": "Q_TOP_3_CUSTOMERS_PCT",
                    "value_numeric": 22
                },
                {
                    "question_code": "Q_DOCUMENTED_PROCESSES",
                    "selected_option_values": ["FULLY_DOCUMENTED"]
                },
                {
                    "question_code": "Q_CRM_SYSTEM",
                    "selected_option_values": ["YES"]
                },
                {
                    "question_code": "Q_FINANCIAL_RECORDS",
                    "selected_option_values": ["PROFESSIONAL"]
                },
                {
                    "question_code": "Q_RECURRING_REVENUE_PCT",
                    "value_numeric": 75
                },
                {
                    "question_code": "Q_GROSS_MARGIN",
                    "value_numeric": 65
                },
                {
                    "question_code": "Q_REVENUE_TREND",
                    "selected_option_values": ["STRONG_GROWTH"]
                },
            ]
        }

        response = client.post(f"/api/v1/standard/projects/{project_id}/answers", json=answers_payload)
        assert response.status_code == 200

        data = response.json()
        assert data["answers_saved"] == 10
        assert data["message"] == "Answers saved successfully"

    def test_get_answers(self, client):
        """Test retrieving answers"""
        # Create project and submit answers
        project_response = client.post("/api/v1/standard/projects", json={
            "name": "Test Business",
            "industry": "saas",
            "financial_inputs": [{"year": 0, "revenue": 500000}]
        })
        project_id = project_response.json()["id"]

        # Submit some answers
        client.post(f"/api/v1/standard/projects/{project_id}/answers", json={
            "answers": [
                {"question_code": "Q_OWNER_ROLE", "selected_option_values": ["FULLY_DELEGATED"]},
                {"question_code": "Q_TOP_CUSTOMER_PCT", "value_numeric": 15}
            ]
        })

        # Retrieve answers
        response = client.get(f"/api/v1/standard/projects/{project_id}/answers")
        assert response.status_code == 200

        data = response.json()
        assert len(data["answers"]) == 2

    def test_compute_score(self, client):
        """Test scorecard computation"""
        # Create project
        project_response = client.post("/api/v1/standard/projects", json={
            "name": "High-Quality Business",
            "industry": "saas",
            "financial_inputs": [{"year": 0, "revenue": 1000000, "ebitda": 300000}]
        })
        project_id = project_response.json()["id"]

        # Submit high-quality answers (should result in good score)
        high_quality_answers = {
            "answers": [
                {"question_code": "Q_OWNER_ROLE", "selected_option_values": ["FULLY_DELEGATED"]},
                {"question_code": "Q_MANAGEMENT_TEAM", "selected_option_values": ["YES"]},
                {"question_code": "Q_KEY_RELATIONSHIPS", "selected_option_values": ["NO_DEPENDENCY"]},
                {"question_code": "Q_TOP_CUSTOMER_PCT", "value_numeric": 5},
                {"question_code": "Q_TOP_3_CUSTOMERS_PCT", "value_numeric": 15},
                {"question_code": "Q_CUSTOMER_CONTRACTS", "selected_option_values": ["LONG_TERM"]},
                {"question_code": "Q_DOCUMENTED_PROCESSES", "selected_option_values": ["FULLY_DOCUMENTED"]},
                {"question_code": "Q_TECHNOLOGY_SYSTEMS", "selected_option_values": ["ADVANCED"]},
                {"question_code": "Q_CRM_SYSTEM", "selected_option_values": ["YES"]},
                {"question_code": "Q_FINANCIAL_RECORDS", "selected_option_values": ["AUDITED"]},
                {"question_code": "Q_RECURRING_REVENUE_PCT", "value_numeric": 85},
                {"question_code": "Q_GROSS_MARGIN", "value_numeric": 75},
                {"question_code": "Q_REVENUE_TREND", "selected_option_values": ["STRONG_GROWTH"]},
                {"question_code": "Q_MARKET_POSITION", "selected_option_values": ["MARKET_LEADER"]},
                {"question_code": "Q_COMPETITIVE_ADVANTAGE", "selected_option_values": ["STRONG_ADVANTAGE"]},
            ]
        }

        client.post(f"/api/v1/standard/projects/{project_id}/answers", json=high_quality_answers)

        # Compute score
        response = client.post(f"/api/v1/standard/projects/{project_id}/score")
        assert response.status_code == 200

        data = response.json()
        assert "total_score" in data
        assert "rating" in data
        assert "adjustment_factor" in data
        assert "dimensions" in data

        # High-quality answers should result in A or B rating
        assert data["rating"] in ["A", "B"]
        assert data["total_score"] >= 65

        # Check dimensions
        assert len(data["dimensions"]) == 5

    def test_standard_valuation(self, client):
        """Test Standard Valuation computation"""
        # Create project with financials
        project_response = client.post("/api/v1/standard/projects", json={
            "name": "Test Valuation Business",
            "industry": "saas",
            "financial_inputs": [
                {"year": 0, "revenue": 1000000, "ebitda": 250000, "total_assets": 500000, "total_liabilities": 100000}
            ]
        })
        project_id = project_response.json()["id"]

        # Submit answers
        answers = {
            "answers": [
                {"question_code": "Q_OWNER_ROLE", "selected_option_values": ["OCCASIONAL_OVERSIGHT"]},
                {"question_code": "Q_MANAGEMENT_TEAM", "selected_option_values": ["YES"]},
                {"question_code": "Q_KEY_RELATIONSHIPS", "selected_option_values": ["LOW_DEPENDENCY"]},
                {"question_code": "Q_TOP_CUSTOMER_PCT", "value_numeric": 12},
                {"question_code": "Q_TOP_3_CUSTOMERS_PCT", "value_numeric": 30},
                {"question_code": "Q_CUSTOMER_CONTRACTS", "selected_option_values": ["MEDIUM_TERM"]},
                {"question_code": "Q_DOCUMENTED_PROCESSES", "selected_option_values": ["MOSTLY_DOCUMENTED"]},
                {"question_code": "Q_TECHNOLOGY_SYSTEMS", "selected_option_values": ["MODERN"]},
                {"question_code": "Q_CRM_SYSTEM", "selected_option_values": ["YES"]},
                {"question_code": "Q_FINANCIAL_RECORDS", "selected_option_values": ["PROFESSIONAL"]},
                {"question_code": "Q_RECURRING_REVENUE_PCT", "value_numeric": 60},
                {"question_code": "Q_GROSS_MARGIN", "value_numeric": 50},
                {"question_code": "Q_REVENUE_TREND", "selected_option_values": ["MODERATE_GROWTH"]},
                {"question_code": "Q_MARKET_POSITION", "selected_option_values": ["STRONG_POSITION"]},
                {"question_code": "Q_COMPETITIVE_ADVANTAGE", "selected_option_values": ["MODERATE_ADVANTAGE"]},
            ]
        }

        client.post(f"/api/v1/standard/projects/{project_id}/answers", json=answers)

        # Compute score
        score_response = client.post(f"/api/v1/standard/projects/{project_id}/score")
        assert score_response.status_code == 200

        # Run Standard Valuation
        response = client.post(f"/api/v1/standard/projects/{project_id}/valuation")
        assert response.status_code == 200

        data = response.json()
        assert "baseline_valuation" in data
        assert "score" in data
        assert "adjusted_valuation" in data

        # Verify adjustment was applied
        baseline_mid = data["baseline_valuation"]["value_mid"]
        adjusted_mid = data["adjusted_valuation"]["value_mid"]
        adjustment_factor = data["score"]["adjustment_factor"]

        # Allow small floating point variance
        expected_adjusted = baseline_mid * adjustment_factor
        assert abs(adjusted_mid - expected_adjusted) < 1.0

    def test_generate_standard_report(self, client):
        """Test Standard report generation"""
        # Create complete project flow
        project_response = client.post("/api/v1/standard/projects", json={
            "name": "Complete Test Business",
            "industry": "saas",
            "description": "Full flow test",
            "financial_inputs": [
                {"year": 0, "revenue": 750000, "ebitda": 200000, "net_profit": 150000}
            ]
        })
        project_id = project_response.json()["id"]

        # Submit answers
        client.post(f"/api/v1/standard/projects/{project_id}/answers", json={
            "answers": [
                {"question_code": "Q_OWNER_ROLE", "selected_option_values": ["PART_TIME_STRATEGIC"]},
                {"question_code": "Q_MANAGEMENT_TEAM", "selected_option_values": ["YES"]},
                {"question_code": "Q_TOP_CUSTOMER_PCT", "value_numeric": 18},
                {"question_code": "Q_TOP_3_CUSTOMERS_PCT", "value_numeric": 40},
                {"question_code": "Q_DOCUMENTED_PROCESSES", "selected_option_values": ["MOSTLY_DOCUMENTED"]},
                {"question_code": "Q_CRM_SYSTEM", "selected_option_values": ["YES"]},
                {"question_code": "Q_FINANCIAL_RECORDS", "selected_option_values": ["PROFESSIONAL"]},
                {"question_code": "Q_RECURRING_REVENUE_PCT", "value_numeric": 55},
                {"question_code": "Q_GROSS_MARGIN", "value_numeric": 45},
                {"question_code": "Q_REVENUE_TREND", "selected_option_values": ["MODERATE_GROWTH"]},
            ]
        })

        # Compute score
        client.post(f"/api/v1/standard/projects/{project_id}/score")

        # Run valuation
        client.post(f"/api/v1/standard/projects/{project_id}/valuation")

        # Generate report
        response = client.post(f"/api/v1/standard/projects/{project_id}/report")
        assert response.status_code == 200

        data = response.json()
        assert "report_id" in data
        assert "content" in data
        assert data["format"] == "markdown"

        # Verify report content
        content = data["content"]
        assert "Exit Ready MPSP" in content
        assert "Complete Test Business" in content
        assert "Scorecard" in content
        assert "Valuation Results" in content
        assert "Recommendations" in content

    def test_end_to_end_standard_flow(self, client):
        """Test complete Standard Valuation Flow end-to-end"""
        # Step 1: Create Standard project
        project_data = {
            "name": "End-to-End Test Business",
            "industry": "technology",
            "description": "Testing complete flow",
            "financial_inputs": [
                {"year": 0, "revenue": 2000000, "ebitda": 500000, "net_profit": 400000, "total_assets": 800000, "total_liabilities": 200000},
                {"year": 1, "revenue": 1600000, "ebitda": 400000},
                {"year": 2, "revenue": 1300000, "ebitda": 320000}
            ]
        }

        create_response = client.post("/api/v1/standard/projects", json=project_data)
        assert create_response.status_code == 201
        project_id = create_response.json()["id"]

        # Step 2: Submit answers
        answers_data = {
            "answers": [
                {"question_code": "Q_OWNER_ROLE", "selected_option_values": ["FULLY_DELEGATED"]},
                {"question_code": "Q_MANAGEMENT_TEAM", "selected_option_values": ["YES"]},
                {"question_code": "Q_KEY_RELATIONSHIPS", "selected_option_values": ["NO_DEPENDENCY"]},
                {"question_code": "Q_TOP_CUSTOMER_PCT", "value_numeric": 8},
                {"question_code": "Q_TOP_3_CUSTOMERS_PCT", "value_numeric": 20},
                {"question_code": "Q_CUSTOMER_CONTRACTS", "selected_option_values": ["LONG_TERM"]},
                {"question_code": "Q_DOCUMENTED_PROCESSES", "selected_option_values": ["FULLY_DOCUMENTED"]},
                {"question_code": "Q_TECHNOLOGY_SYSTEMS", "selected_option_values": ["ADVANCED"]},
                {"question_code": "Q_CRM_SYSTEM", "selected_option_values": ["YES"]},
                {"question_code": "Q_FINANCIAL_RECORDS", "selected_option_values": ["AUDITED"]},
                {"question_code": "Q_RECURRING_REVENUE_PCT", "value_numeric": 80},
                {"question_code": "Q_GROSS_MARGIN", "value_numeric": 70},
                {"question_code": "Q_REVENUE_TREND", "selected_option_values": ["STRONG_GROWTH"]},
                {"question_code": "Q_MARKET_POSITION", "selected_option_values": ["MARKET_LEADER"]},
                {"question_code": "Q_COMPETITIVE_ADVANTAGE", "selected_option_values": ["STRONG_ADVANTAGE"]},
                {"question_code": "Q_KEY_EMPLOYEES", "selected_option_values": ["DISTRIBUTED"]},
                {"question_code": "Q_EMPLOYEE_RETENTION", "selected_option_values": ["EXCELLENT_TENURE"]},
                {"question_code": "Q_LEGAL_STRUCTURE", "selected_option_values": ["OPTIMIZED"]},
                {"question_code": "Q_IP_PROTECTION", "selected_option_values": ["COMPREHENSIVE"]},
                {"question_code": "Q_COMPLIANCE_ISSUES", "selected_option_values": ["YES"]},
            ]
        }

        answer_response = client.post(f"/api/v1/standard/projects/{project_id}/answers", json=answers_data)
        assert answer_response.status_code == 200
        assert answer_response.json()["answers_saved"] == 20

        # Step 3: Compute scorecard
        score_response = client.post(f"/api/v1/standard/projects/{project_id}/score")
        assert score_response.status_code == 200
        score_data = score_response.json()
        assert score_data["rating"] == "A"  # Should be A with these high-quality answers

        # Step 4: Run Standard Valuation
        valuation_response = client.post(f"/api/v1/standard/projects/{project_id}/valuation")
        assert valuation_response.status_code == 200
        valuation_data = valuation_response.json()

        assert valuation_data["score"]["rating"] == "A"
        assert valuation_data["score"]["adjustment_factor"] == 1.10

        # Verify valuation was adjusted
        assert valuation_data["adjusted_valuation"]["value_mid"] > valuation_data["baseline_valuation"]["value_mid"]

        # Step 5: Generate report
        report_response = client.post(f"/api/v1/standard/projects/{project_id}/report")
        assert report_response.status_code == 200

        report_content = report_response.json()["content"]
        assert "Exit Ready MPSP" in report_content
        assert "End-to-End Test Business" in report_content
        assert "Rating: A" in report_content

        print("\n✓ End-to-end Standard Flow test completed successfully!")
