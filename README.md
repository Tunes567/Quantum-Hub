# Quantum Hub SMS

A modern SMS management platform built with Next.js.

## Getting Started

First, install dependencies:

```bash
npm install
# or
yarn install
```

Then, run the development server:

```bash
npm run dev
# or
yarn dev
```

Open [http://localhost:3000](http://localhost:3000) with your browser to see the result.

## API Routes

This application includes the following API routes:

- `/api/health` - Health check endpoint
- `/api/hello` - Simple hello world endpoint

## Deployment on Vercel

This application is optimized for deployment on Vercel. Simply push to your GitHub repository and import the project in Vercel.

### Deployment Configuration

When deploying to Vercel, the platform will automatically:

1. Install dependencies with `npm install`
2. Build the application with `npm run build`
3. Deploy the application

No further configuration is required for a basic deployment.

## Previous Flask Version

The project was previously implemented using Flask. The Next.js version offers:

- Better integration with Vercel
- Improved performance with static/server rendering
- Simplified deployment process
- Modern React-based frontend 