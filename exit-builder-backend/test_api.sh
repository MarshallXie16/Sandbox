#!/bin/bash
# Test script for Quick Valuation API

API_URL="http://localhost:8000"

echo "=== Capital Link Exit Builder - API Test ==="
echo ""

# Test 1: Health Check
echo "1. Testing Health Check..."
curl -s "$API_URL/health" | python3 -m json.tool
echo ""
echo ""

# Test 2: Create Quick Valuation
echo "2. Creating Quick Valuation Project..."
RESPONSE=$(curl -s -X POST "$API_URL/api/v1/projects/quick" \
  -H "Content-Type: application/json" \
  -d '{
    "client": {
      "name": "ABC HVAC Services",
      "contact_name": "John Smith",
      "email": "john@abchvac.com",
      "phone": "604-555-1234"
    },
    "project": {
      "business_name": "ABC HVAC Services",
      "industry_code": "238220",
      "location": "Vancouver, BC"
    },
    "financial": {
      "metric_type": "SDE",
      "metric_value": 270000,
      "revenue": 1350000
    }
  }')

echo "$RESPONSE" | python3 -m json.tool
PROJECT_ID=$(echo "$RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['project_id'])")
echo ""
echo "Created Project ID: $PROJECT_ID"
echo ""
echo ""

# Test 3: Get Project Details
echo "3. Getting Project Details..."
curl -s "$API_URL/api/v1/projects/$PROJECT_ID" | python3 -m json.tool
echo ""
echo ""

# Test 4: Get Project Report
echo "4. Getting Project Report (first 50 lines)..."
curl -s "$API_URL/api/v1/projects/$PROJECT_ID/report" | python3 -c "import sys, json; data = json.load(sys.stdin); print(data['content'][:2000] + '...')"
echo ""
echo ""

echo "=== Test Complete ==="
echo "Full API documentation: $API_URL/docs"
