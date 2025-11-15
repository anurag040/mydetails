#!/bin/bash

# Payments Hub Dashboard - Installation & Startup Script
# This script helps you get the Angular application running quickly

echo "🚀 Payments Hub Dashboard - Startup Script"
echo "=========================================="
echo ""

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed."
    echo "Please install Node.js 18+ from https://nodejs.org/"
    exit 1
fi

echo "✅ Node.js version: $(node --version)"
echo "✅ npm version: $(npm --version)"
echo ""

# Step 1: Install dependencies
echo "📦 Step 1: Installing dependencies..."
echo "This may take a few minutes..."
npm install

if [ $? -ne 0 ]; then
    echo "❌ Installation failed. Please check your npm connection."
    exit 1
fi

echo "✅ Dependencies installed successfully!"
echo ""

# Step 2: Start development server
echo "🔥 Step 2: Starting development server..."
echo "The application will open automatically in your browser..."
echo ""
echo "Opening at http://localhost:4200"
echo "Press Ctrl+C to stop the server"
echo ""

npm start

# The app is now running!
