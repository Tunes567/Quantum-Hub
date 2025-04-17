#!/bin/bash

# Display Python version
python --version

# Display pip version
pip --version

# Install dependencies
pip install -r vercel-requirements.txt

# Create any necessary directories
mkdir -p .vercel_build_output

# Display installed packages for debugging
pip list

# Success message
echo "Build completed successfully!" 