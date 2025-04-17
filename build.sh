#!/bin/bash

echo "Starting build process..."

# Display Python version
echo "Python version: $(python --version)"

# Display pip version
echo "Pip version: $(pip --version)"

# Create necessary directories
echo "Creating directories..."
mkdir -p api/static
mkdir -p api/templates

# Install dependencies (only Flask)
echo "Installing minimal dependencies..."
pip install flask==2.2.3

# Copy static file if it doesn't exist
if [ ! -f "api/static/index.html" ]; then
  echo "Creating static test file..."
  echo '<!DOCTYPE html><html><head><title>Test</title></head><body><h1>Static Test</h1></body></html>' > api/static/index.html
fi

# List files for verification
echo "API directory contents:"
ls -la api/

# Success message
echo "Build completed successfully!" 