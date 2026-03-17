#!/bin/bash
# Video Compliance Framework - Quick Start Script (macOS/Linux)

echo ""
echo "========================================"
echo "Video Compliance Framework - Quick Start"
echo "========================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed or not in PATH"
    echo "Please install Python 3.8+ from https://python.org"
    exit 1
fi

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "ERROR: Node.js is not installed or not in PATH"
    echo "Please install Node.js from https://nodejs.org"
    exit 1
fi

echo "✓ Python and Node.js found"
echo ""

# Install Python dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to install Python dependencies"
    exit 1
fi
echo "✓ Python dependencies installed"
echo ""

# Install Frontend dependencies
echo "Installing frontend dependencies..."
cd frontend
npm install
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to install frontend dependencies"
    exit 1
fi
echo "✓ Frontend dependencies installed"
cd ..
echo ""

# Create .env.local for frontend
echo "Creating frontend environment configuration..."
if [ ! -f frontend/.env.local ]; then
    echo "REACT_APP_API_URL=http://localhost:5000" > frontend/.env.local
    echo "✓ Frontend environment configured"
else
    echo "✓ Frontend environment already configured"
fi
echo ""

# Create directories
mkdir -p uploads
mkdir -p preprocessed_output
echo "✓ Output directories created"
echo ""

echo "========================================"
echo "Setup Complete!"
echo "========================================"
echo ""
echo "Next steps:"
echo ""
echo "1. START BACKEND SERVER (in one terminal):"
echo "   python app.py"
echo ""
echo "2. START FRONTEND (in another terminal):"
echo "   cd frontend"
echo "   npm start"
echo ""
echo "3. OPEN BROWSER:"
echo "   http://localhost:3000"
echo ""
echo "Documentation:"
echo "  - SETUP_GUIDE.md - Complete setup guide"
echo "  - BACKEND_API.md - API documentation"
echo "  - frontend/README.md - Frontend documentation"
echo ""
