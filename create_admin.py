from supabase import create_client
import os
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash

# Load environment variables
load_dotenv()

# Initialize Supabase client
supabase_url = os.getenv('SUPABASE_URL')
supabase_key = os.getenv('SUPABASE_KEY')
supabase = create_client(supabase_url, supabase_key)

# Create admin user
admin_data = {
    'username': 'admin',
    'email': 'admin@example.com',
    'password': generate_password_hash('admin123'),
    'credits': 1000.0,
    'is_admin': True,
    'sms_rate': 0.05,
    'role': 'admin'
}

# Insert user into database
response = supabase.table('users').insert(admin_data).execute()

if response.data:
    print("Admin user created successfully!")
else:
    print("Error creating admin user:", response.error) 