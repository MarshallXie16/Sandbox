# 🚀 Quick Start Guide - Exit Builder Backend

## Prerequisites Checklist

- [ ] Python 3.11+ installed
- [ ] PostgreSQL 12+ installed and running
- [ ] Git installed (optional)

## 5-Minute Setup

### Step 1: Run Setup Script
```bash
cd exit-builder-backend
./setup.sh
```

This will:
- Create virtual environment
- Install all dependencies
- Create .env file from template

### Step 2: Configure Database
Edit `.env` file:
```bash
DATABASE_URL=postgresql://YOUR_USER:YOUR_PASSWORD@localhost:5432/exit_builder
```

### Step 3: Create Database
```bash
# Using psql
psql -U postgres
CREATE DATABASE exit_builder;
\q

# Or using createdb command
createdb -U postgres exit_builder
```

### Step 4: Run Migrations
```bash
source venv/bin/activate  # Activate virtual environment
alembic upgrade head
```

### Step 5: Seed Data
```bash
python seed_data.py
```

### Step 6: Start Server
```bash
./run.sh
```

Server will start at: **http://localhost:8000**

### Step 7: Test API
In a new terminal:
```bash
./test_api.sh
```

## ✅ Verification

Visit these URLs to verify everything is working:

- **API Root**: http://localhost:8000
- **Health Check**: http://localhost:8000/health
- **API Documentation**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc

## 🎯 Your First Valuation

### Using curl:
```bash
curl -X POST "http://localhost:8000/api/v1/projects/quick" \
  -H "Content-Type: application/json" \
  -d '{
    "client": {
      "name": "My Business",
      "email": "owner@mybusiness.com"
    },
    "project": {
      "business_name": "My Business",
      "industry_code": "238220",
      "location": "Vancouver, BC"
    },
    "financial": {
      "metric_type": "SDE",
      "metric_value": 250000,
      "revenue": 1200000
    }
  }'
```

### Using API Docs (Easier!):
1. Go to http://localhost:8000/docs
2. Click on `POST /api/v1/projects/quick`
3. Click "Try it out"
4. Use the sample JSON below
5. Click "Execute"

### Sample Request:
```json
{
  "client": {
    "name": "ABC HVAC",
    "contact_name": "John Doe",
    "email": "john@abchvac.com",
    "phone": "604-123-4567"
  },
  "project": {
    "business_name": "ABC HVAC",
    "industry_code": "238220",
    "location": "Vancouver, BC"
  },
  "financial": {
    "metric_type": "SDE",
    "metric_value": 270000,
    "revenue": 1350000
  }
}
```

### Expected Response:
```json
{
  "project_id": "uuid-here",
  "client_id": "uuid-here",
  "report_id": "uuid-here",
  "valuation_summary": {
    "recommended_value_low": 756000,
    "recommended_value_mid": 864000,
    "recommended_value_high": 972000,
    "currency": "CAD"
  }
}
```

## 📊 Available Industries

The system comes pre-loaded with multiples for:

| Industry | Code | Metric Types |
|----------|------|--------------|
| HVAC Services | 238220 | SDE, EBITDA |
| Restaurants | 722511 | SDE, EBITDA |
| Management Consulting | 541611 | SDE, EBITDA |
| Retail (General) | 445110 | SDE, EBITDA |

## 🔧 Common Issues

### Issue: Database connection error
**Solution**:
- Verify PostgreSQL is running: `pg_isready`
- Check DATABASE_URL in `.env`
- Ensure database exists: `psql -l | grep exit_builder`

### Issue: Module not found
**Solution**:
```bash
source venv/bin/activate
pip install -r requirements.txt
```

### Issue: Alembic error
**Solution**:
```bash
# Reset and rerun migrations
alembic downgrade base
alembic upgrade head
python seed_data.py
```

### Issue: Port 8000 already in use
**Solution**:
```bash
# Use a different port
uvicorn app.main:app --port 8001
```

## 📖 Next Steps

1. **Explore API Docs**: http://localhost:8000/docs
2. **Read Full Documentation**: See `README.md`
3. **View Project Overview**: See `PROJECT_OVERVIEW.md`
4. **Run Tests**: `pytest`
5. **Customize**: Add your own industry multiples in `seed_data.py`

## 🎓 Learning the Codebase

**Start with these files:**

1. `app/main.py` - Application entry point
2. `app/api/v1/routes/quick.py` - API endpoints
3. `app/services/quick_flow.py` - Business logic orchestration
4. `app/services/valuation_core.py` - Valuation algorithm
5. `app/models/` - Database models

## 💡 Tips

- Use the interactive API docs at `/docs` for testing
- Check `seed_data.py` to see what data is available
- Look at `tests/` for usage examples
- All IDs are UUIDs for better security
- Reports are in Markdown format (easy to convert to PDF later)

## 🆘 Need Help?

1. Check the console output for detailed error messages
2. Review the logs when running the server
3. Look at the test files for examples
4. Check `PROJECT_OVERVIEW.md` for architecture details

---

**Ready to build!** 🎉
