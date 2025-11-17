#!/bin/bash
# Setup script for Project Companion

set -e

echo "🌱 Setting up Project Companion..."

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install Python dependencies
echo "Installing Python dependencies..."
pip install --upgrade pip
pip install -e ".[dev]"

# Install Playwright (optional)
read -p "Install Playwright for dynamic scanning? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    playwright install chromium
fi

# Setup UI
if [ -d "ui" ]; then
    echo "Setting up UI..."
    cd ui
    if [ ! -d "node_modules" ]; then
        npm install
    fi
    cd ..
fi

# Create necessary directories
mkdir -p knowledge audit

echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Activate virtual environment: source venv/bin/activate"
echo "2. Start the backend: uvicorn app.main:app --reload"
echo "3. Start the UI (in another terminal): cd ui && npm run dev"
echo "4. Scan a repository: companion scan examples/sample_repo"

