#!/bin/bash

# Animal Detection App - Quick Start Script

echo "========================================"
echo "🐾 Animal Detection App - Quick Start"
echo "========================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.7 or higher."
    exit 1
fi

echo "✓ Python 3 detected: $(python3 --version)"
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo "✓ Virtual environment created"
else
    echo "✓ Virtual environment already exists"
fi

echo ""

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

echo ""

# Install dependencies
echo "Installing dependencies..."
pip install -q --upgrade pip
pip install -q -r requirements.txt
echo "✓ Dependencies installed"

echo ""
echo "========================================"
echo "Setup complete! Choose an option:"
echo "========================================"
echo ""
echo "1. Start Web Interface (Recommended)"
echo "2. CLI Help"
echo "3. Exit"
echo ""
read -p "Enter your choice (1-3): " choice

case $choice in
    1)
        echo ""
        echo "Starting web server..."
        echo "Open your browser and navigate to: http://localhost:5000"
        echo ""
        python src/app.py
        ;;
    2)
        echo ""
        python main.py --help
        ;;
    3)
        echo "Goodbye!"
        exit 0
        ;;
    *)
        echo "Invalid choice. Run 'python src/app.py' for web interface or 'python main.py --help' for CLI usage."
        ;;
esac
