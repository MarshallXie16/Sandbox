#!/bin/bash
# Initialize database with migrations and seed data

set -e

echo "🚀 Initializing IndieStack CRM Database..."

# Check if virtual environment is activated
if [ -z "$VIRTUAL_ENV" ]; then
    echo "⚠️  Virtual environment not detected. Activating..."
    source venv/bin/activate
fi

# Check if .env file exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found. Copying from .env.example..."
    cp .env.example .env
    echo "✅ Please update .env with your database credentials"
    exit 1
fi

# Run migrations
echo "📦 Running database migrations..."
alembic upgrade head

# Seed default pipelines
echo "🌱 Seeding default pipelines and stages..."
python -m app.db.seed_data

echo "✅ Database initialization complete!"
echo ""
echo "Next steps:"
echo "  1. Start the server: uvicorn app.main:app --reload"
echo "  2. Visit API docs: http://localhost:8000/docs"
