#!/bin/bash
# EgySentiment Docker & Airflow Setup Script

set -e

echo "======================================"
echo "EgySentiment Setup"
echo "======================================"
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    echo "   Visit: https://docs.docker.com/get-docker/"
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    echo "   Visit: https://docs.docker.com/compose/install/"
    exit 1
fi

echo "✓ Docker and Docker Compose are installed"
echo ""

# Check .env file
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found. Creating template..."
    cat > .env << EOF
# Groq API Configuration
GROQ_API_KEY=your_groq_api_key_here

# Airflow Configuration  
AIRFLOW_UID=50000
EOF
    echo "✓ Created .env template"
    echo "❗ Please edit .env and add your Groq API key"
    echo ""
fi

# Create necessary directories
echo "Creating directories..."
mkdir -p data logs dags/. docker src

echo "✓ Directories created"
echo ""

# Set Airflow UID
export AIRFLOW_UID=$(id -u)

# Initialize Airflow database
echo "Initializing Airflow..."
docker-compose up airflow-init

echo ""
echo "✓ Airflow initialized"
echo ""

# Start services
echo "Starting Docker services..."
docker-compose up -d

echo ""
echo "======================================"
echo "✓ Setup Complete!"
echo "======================================"
echo ""
echo "Services running:"
echo "  - Airflow Webserver: http://localhost:8080"
echo "    Username: admin"
echo "    Password: admin"
echo ""
echo "Next steps:"
echo "  1. Access Airflow UI at http://localhost:8080"
echo "  2. Enable the DAG: egy_sentiment_daily_collection"
echo "  3. Or run historical scraper:"
echo "     docker-compose run scraper python src/historical_scraper.py"
echo ""
echo "To check logs:"
echo "  docker-compose logs -f airflow-scheduler"
echo ""
echo "To stop services:"
echo "  docker-compose down"
echo ""
