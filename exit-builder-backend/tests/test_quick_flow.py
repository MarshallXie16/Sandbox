"""
Tests for Quick Valuation Flow
"""
import pytest


class TestQuickFlow:
    """Test suite for Quick Valuation Flow"""

    def test_create_quick_project(self, client):
        """Test creating a Quick project"""
        payload = {
            "name": "Quick Test Business",
            "industry": "saas",
            "description": "A quick valuation test",
            "financial_inputs": [
                {
                    "year": 0,
                    "revenue": 1000000,
                    "net_profit": 200000,
                    "ebitda": 300000,
                    "total_assets": 500000,
                    "total_liabilities": 150000
                }
            ]
        }

        response = client.post("/api/v1/quick/projects", json=payload)
        assert response.status_code == 201

        data = response.json()
        assert data["name"] == "Quick Test Business"
        assert data["project_type"] == "QUICK"
        assert data["industry"] == "saas"

    def test_quick_valuation(self, client):
        """Test running Quick Valuation"""
        # Create project
        project_response = client.post("/api/v1/quick/projects", json={
            "name": "Valuation Test",
            "industry": "ecommerce",
            "financial_inputs": [
                {"year": 0, "revenue": 500000, "ebitda": 100000}
            ]
        })
        project_id = project_response.json()["id"]

        # Run valuation
        response = client.post(f"/api/v1/quick/projects/{project_id}/valuation")
        assert response.status_code == 200

        data = response.json()
        assert "value_low" in data
        assert "value_mid" in data
        assert "value_high" in data
        assert "primary_method" in data

        # Verify valuation is reasonable (should be non-zero)
        assert data["value_mid"] > 0

    def test_quick_report_generation(self, client):
        """Test Quick report generation"""
        # Create and value project
        project_response = client.post("/api/v1/quick/projects", json={
            "name": "Report Test Business",
            "industry": "saas",
            "financial_inputs": [
                {"year": 0, "revenue": 750000, "ebitda": 180000, "net_profit": 120000}
            ]
        })
        project_id = project_response.json()["id"]

        # Run valuation
        client.post(f"/api/v1/quick/projects/{project_id}/valuation")

        # Generate report
        response = client.post(f"/api/v1/quick/projects/{project_id}/report")
        assert response.status_code == 200

        data = response.json()
        assert "report_id" in data
        assert "content" in data
        assert data["format"] == "markdown"

        # Verify content
        content = data["content"]
        assert "Quick Valuation Report" in content
        assert "Report Test Business" in content

    def test_end_to_end_quick_flow(self, client):
        """Test complete Quick flow end-to-end"""
        # Create project
        create_response = client.post("/api/v1/quick/projects", json={
            "name": "E2E Quick Test",
            "industry": "technology",
            "financial_inputs": [
                {
                    "year": 0,
                    "revenue": 2000000,
                    "ebitda": 600000,
                    "net_profit": 450000,
                    "total_assets": 1000000,
                    "total_liabilities": 300000
                }
            ]
        })
        assert create_response.status_code == 201
        project_id = create_response.json()["id"]

        # Run valuation
        valuation_response = client.post(f"/api/v1/quick/projects/{project_id}/valuation")
        assert valuation_response.status_code == 200
        valuation_data = valuation_response.json()
        assert valuation_data["value_mid"] > 0

        # Generate report
        report_response = client.post(f"/api/v1/quick/projects/{project_id}/report")
        assert report_response.status_code == 200

        print("\n✓ End-to-end Quick Flow test completed successfully!")
