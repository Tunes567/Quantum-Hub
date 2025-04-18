// Script to update admin password in Supabase database
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

async function updateAdminPassword() {
  try {
    // Hash the password
    const salt = await bcrypt.genSalt(10);
    const hashedPassword = await bcrypt.hash('admin123', salt);

    // Update admin user's password
    const { data, error } = await supabase
      .from('users')
      .update({ password: hashedPassword })
      .eq('username', 'admin')
      .select();

    if (error) {
      console.error('Error updating admin password:', error);
    } else {
      console.log('Admin password updated successfully!');
      console.log('You can now login with:');
      console.log('Username: admin');
      console.log('Password: admin123');
    }
  } catch (error) {
    console.error('Unexpected error:', error);
  }
}

updateAdminPassword(); 