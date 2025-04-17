# Vercel Deployment Troubleshooting

This document provides instructions for deploying the Quantum Hub SMS application on Vercel and troubleshooting common issues.

## Prerequisites

- Vercel account
- GitHub repository with the application code

## Deployment Steps

1. Connect your GitHub repository to Vercel
2. Configure the following settings:
   - Build command: `sh build.sh`
   - Output directory: `.`
   - Development command: None (leave blank)
   - Install command: None (leave blank)

3. Add all required environment variables in the Vercel dashboard:
   - `SECRET_KEY`
   - `FLASK_APP`
   - `FLASK_ENV` (set to "production")
   - `SUPABASE_URL` (if using Supabase)
   - `SUPABASE_KEY` (if using Supabase)
   - `SMPP_HOST` (if using SMPP)
   - `SMPP_PORT` (if using SMPP)
   - `SMPP_USERNAME` (if using SMPP)
   - `SMPP_PASSWORD` (if using SMPP)

## Common Issues and Solutions

### 500 Internal Server Error

If you encounter a 500 Internal Server Error (FUNCTION_INVOCATION_FAILED):

1. Check the function logs in the Vercel dashboard (Functions tab)
2. Verify all required environment variables are set
3. Make sure all dependencies are properly listed in `api/requirements.txt`
4. Check for syntax errors or exceptions in your code

### Function Timeout

If your function times out:

1. Optimize your code to run faster
2. Increase the function timeout in `vercel.json` (currently set to 30 seconds)

### Missing Dependencies

If you see import errors:

1. Ensure all required packages are listed in `api/requirements.txt`
2. Verify package versions are compatible

## Local Testing

To test the serverless function locally before deploying:

1. Install the Vercel CLI: `npm install -g vercel`
2. Run `vercel dev` in the project directory
3. Test the API endpoints at `http://localhost:3000/api/...`

## Debugging Tips

- Add detailed logging in your serverless functions
- Use environment-specific configuration to differentiate between local and production environments
- Handle exceptions properly and return meaningful error messages

## Contact

If you continue to experience issues after trying these steps, please reach out for additional support. 