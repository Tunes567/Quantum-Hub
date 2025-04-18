// Script to create an admin user in Supabase database
const { createClient } = require('@supabase/supabase-js');
const bcrypt = require('bcryptjs');
require('dotenv').config({ path: '.env.local' });

// Initialize Supabase client
const supabaseUrl = process.env.SUPABASE_URL;
const supabaseKey = process.env.SUPABASE_KEY;

if (!supabaseUrl || !supabaseKey) {
  console.error('Supabase credentials are missing. Please check your .env.local file.');
  process.exit(1);
}

const supabase = createClient(supabaseUrl, supabaseKey);

async function createAdminUser() {
  try {
    // Hash the password
    const salt = await bcrypt.genSalt(10);
    const hashedPassword = await bcrypt.hash('admin123', salt);

    // Check if admin user already exists
    const { data: existingUser, error: queryError } = await supabase
      .from('users')
      .select('id')
      .eq('username', 'admin')
      .single();

    if (queryError && queryError.code !== 'PGRST116') { // PGRST116 means no rows returned
      console.error('Error checking for existing admin:', queryError);
      return;
    }

    if (existingUser) {
      console.log('Admin user already exists with ID:', existingUser.id);
      return;
    }

    // Create admin user
    const adminData = {
      username: 'admin',
      email: 'admin@example.com',
      password: hashedPassword,
      credits: 1000.0,
      is_admin: true,
      sms_rate: 0.05,
      role: 'admin'
    };

    // Insert user into database
    const { data, error } = await supabase.from('users').insert([adminData]);

    if (error) {
      console.error('Error creating admin user:', error);
    } else {
      console.log('Admin user created successfully!');
    }
  } catch (error) {
    console.error('Unexpected error:', error);
  }
}

createAdminUser(); 