#!/bin/bash
# Setup script for Exit Builder backend

echo "=== Capital Link Exit Builder - Backend Setup ==="
echo ""

# Create virtual environment
echo "1. Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "2. Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "3. Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "4. Creating .env file from template..."
    cp .env.example .env
    echo "   ⚠️  Please update .env with your database credentials"
else
    echo "4. .env file already exists, skipping..."
fi

echo ""
echo "=== Setup Complete! ==="
echo ""
echo "Next steps:"
echo "  1. Update .env with your PostgreSQL credentials"
echo "  2. Create the database: createdb exit_builder"
echo "  3. Run migrations: alembic upgrade head"
echo "  4. Seed data: python seed_data.py"
echo "  5. Start server: ./run.sh or python -m app.main"
echo ""
echo "Documentation: http://localhost:8000/docs"
