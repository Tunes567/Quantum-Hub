# Vercel Troubleshooting Guide

## Minimal Deployment Setup

We've simplified the project to the bare minimum to isolate deployment issues:

- Simplified `api/index.py` with basic routes
- Minimal `requirements.txt` with only Flask
- Basic `vercel.json` configuration
- Simple build script

## Common Vercel Deployment Issues

### 1. Serverless Function Size Limit

Vercel has a 50MB limit for serverless functions. Check if you're exceeding this limit.

### 2. Build Command Issues

Make sure your build command is correctly specified in the Vercel dashboard:
- Set the build command to: `sh build.sh`

### 3. Project Structure

Vercel expects a specific structure for Python projects:
- API routes should be in an `/api` directory
- Each function should export a Flask app named `app`

### 4. Environment Variables

Set any required environment variables in the Vercel dashboard.

### 5. Vercel-specific Issues

- Try clearing the Vercel cache: Go to your project settings → "Clear Cache"
- Ensure your Vercel account is properly configured
- Check if your repository has any deployment restrictions

## Next Steps if Issues Persist

1. Try creating a new Vercel project with a different name
2. Deploy a sample Flask template from Vercel's examples
3. Contact Vercel support and provide the error ID 