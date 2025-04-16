# SMS Hub - SMTP SMS Gateway

A comprehensive SMS platform for sending and managing SMS messages for businesses and organizations.

## Features

- User authentication (register/login)
- SMTP configuration management
- SMS message sending
- Modern, responsive UI
- Secure password handling

## Setup

1. Clone the repository
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Create a `.env` file with your secret key:
   ```
   SECRET_KEY=your-secret-key-here
   ```
5. Run the application:
   ```bash
   python app.py
   ```

## Usage

1. Register a new account with your SMTP credentials
2. Log in to your account
3. Use the dashboard to send SMS messages
4. Messages will be sent through your configured SMTP server

## SMTP Configuration

When registering, you'll need to provide:
- SMTP Server address
- SMTP Port (usually 587 for TLS)
- SMTP Username
- SMTP Password

## Security Notes

- All passwords are securely hashed
- SMTP credentials are stored in the database
- Use HTTPS in production
- Keep your secret key secure

## License

MIT License

## Deployment to Vercel and Supabase

This guide will help you deploy the SMS Hub application using Vercel for hosting and Supabase for the database.

### Prerequisites

- Vercel account (https://vercel.com)
- Supabase account (https://supabase.com)
- SMS API service provider credentials

### Step 1: Set up Supabase

1. Create a new Supabase project
2. Go to the SQL Editor in your Supabase dashboard
3. Run the SQL commands from `supabase/schema.sql` to create your database tables
4. Save your Supabase URL and anon key from the API settings page

### Step 2: Configure Environment Variables

1. Copy `.env.vercel` to `.env`
2. Run `python generate_secret_key.py` to generate a secure key
3. Update the following environment variables:
   - `SUPABASE_URL`: Your Supabase project URL
   - `SUPABASE_KEY`: Your Supabase anon key
   - `SMS_API_URL`: Your SMS service provider's API URL
   - `SMS_API_KEY`: Your SMS service API key
   - `SMS_SENDER_ID`: Your sender ID or phone number
   - `SECRET_KEY`: The generated secret key

### Step 3: Deploy to Vercel

1. Install Vercel CLI:
   ```
   npm install -g vercel
   ```

2. Log in to Vercel:
   ```
   vercel login
   ```

3. Deploy your project:
   ```
   vercel
   ```

4. When prompted, configure the project:
   - Set the framework to "Other"
   - Set the build command to "pip install -r vercel-requirements.txt"
   - Set the output directory to "."
   - Set the development command to "python vercel_app.py"

5. Visit your deployed site at the provided Vercel URL

### Step 4: Configure Environment Variables in Vercel

1. Go to your project in the Vercel dashboard
2. Navigate to Settings > Environment Variables
3. Add all the variables from your `.env` file
4. Redeploy your application for the changes to take effect

## Handling High Volume (100K Messages Daily)

For high message volume, consider:

1. **Setup Queue Workers:**
   - Create a separate worker service to process message queues
   - Use Vercel Cron Jobs for scheduled tasks

2. **Database Optimization:**
   - Set up proper indexing (already in schema)
   - Consider partitioning the messages table by date
   - Implement archiving for older messages

3. **Scaling:**
   - Monitor your application performance
   - Upgrade your Supabase plan as needed
   - Consider implementing rate limiting

## Monitoring and Maintenance

1. Set up Vercel Analytics to monitor application performance
2. Create regular database backups using Supabase's backup feature
3. Monitor SMS API usage and costs

## Security Considerations

1. All user passwords are stored securely using hash+salt
2. Supabase Row Level Security (RLS) policies protect user data
3. Environment variables secure all sensitive credentials 