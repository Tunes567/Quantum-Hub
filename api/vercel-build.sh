#!/bin/bash

# Print current directory
echo "Current directory: $(pwd)"
echo "Listing files: $(ls -la)"

# Create templates directory if it doesn't exist
mkdir -p templates
echo "Created templates directory"

# Copy templates from project root if they exist
if [ -d "../templates" ]; then
  cp -r ../templates/* templates/
  echo "Copied templates from project root"
fi

# Create static directory if it doesn't exist
mkdir -p static
echo "Created static directory"

# Copy static files if they exist
if [ -d "../static" ]; then
  cp -r ../static/* static/
  echo "Copied static files from project root"
fi

# Print environment for debugging (without sensitive values)
echo "FLASK_APP: ${FLASK_APP:-(not set)}"
echo "SUPABASE_URL set: $(if [ -n "$SUPABASE_URL" ]; then echo "yes"; else echo "no"; fi)"
echo "SMPP_HOST set: $(if [ -n "$SMPP_HOST" ]; then echo "yes"; else echo "no"; fi)"

echo "Build completed successfully" 