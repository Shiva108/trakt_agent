#!/bin/bash

# Trakt Agent Installation Script
# This script sets up the Python environment and installs dependencies

set -e  # Exit on any error

echo "🎬 Trakt Agent Installation"
echo "=============================="
echo ""

# Check for Python 3
echo "📋 Checking system dependencies..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 is not installed."
    echo "   Please install Python 3.8 or higher and try again."
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
echo "✅ Found Python $PYTHON_VERSION"

# Check Python version is 3.8+
if ! python3 -c "import sys; exit(0 if sys.version_info >= (3, 8) else 1)"; then
    echo "❌ Error: Python 3.8+ is required"
    echo "   Current version: $(python3 --version)"
    exit 1
fi

# Check for pip
if ! command -v pip3 &> /dev/null; then
    echo "❌ Error: pip3 is not installed."
    echo "   Please install pip3 and try again."
    exit 1
fi

echo "✅ Found pip3"
echo ""

# Create virtual environment
echo "🔧 Creating Python virtual environment..."
if [ -d "venv" ]; then
    echo "⚠️  Virtual environment already exists. Skipping creation."
else
    python3 -m venv venv
    echo "✅ Virtual environment created"
fi
echo ""

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "📦 Upgrading pip..."
pip install --upgrade pip > /dev/null 2>&1
echo "✅ pip upgraded"
echo ""

# Install dependencies
echo "📦 Installing Python dependencies..."
if [ ! -f "requirements.txt" ]; then
    echo "❌ Error: requirements.txt not found"
    exit 1
fi

pip install -r requirements.txt
echo "✅ Dependencies installed"
echo ""

# Create necessary directories
echo "📁 Creating necessary directories..."
mkdir -p data output
echo "✅ Directories created"
echo ""

echo "=============================="
echo "✅ Installation complete!"
echo ""
echo "Next steps:"
echo "  1. Activate the virtual environment:"
echo "     source venv/bin/activate"
echo ""
echo "  2. Run the setup script:"
echo "     python setup.py"
echo ""
echo "  3. Start using the agent:"
echo "     python cli.py --help"
echo ""
