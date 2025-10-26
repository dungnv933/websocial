#!/bin/bash
# Setup script for SMM Panel Backend

echo "Setting up SMM Panel Backend..."

# Check Python version
python3 --version

# Install dependencies
echo "Installing dependencies..."
pip3 install -r requirements.txt

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "Creating .env file..."
    cp env.example .env
    echo "Please edit .env file with your configuration"
fi

# Create database (if PostgreSQL is available)
echo "Creating database..."
createdb smmpanel 2>/dev/null || echo "Database creation failed or already exists"

# Run migrations
echo "Running database migrations..."
alembic upgrade head

echo "Setup completed!"
echo "To run the application:"
echo "  python3 run.py"
echo "  or"
echo "  uvicorn app.main:app --host 0.0.0.0 --port 8000"

