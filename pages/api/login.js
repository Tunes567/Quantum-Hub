import { createClient } from '@supabase/supabase-js';
import { compare } from 'bcryptjs';

// Initialize Supabase client with the correct environment variables
const supabase = createClient(
  process.env.NEXT_PUBLIC_SUPABASE_URL,
  process.env.SUPABASE_KEY
);

export default async function handler(req, res) {
  console.log('API Route Hit:', req.method);
  console.log('Environment check:', {
    supabaseUrl: process.env.NEXT_PUBLIC_SUPABASE_URL ? 'Set' : 'Not Set',
    supabaseKey: process.env.SUPABASE_KEY ? 'Set' : 'Not Set'
  });
  
  // Enable CORS
  res.setHeader('Access-Control-Allow-Credentials', true);
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET,OPTIONS,PATCH,DELETE,POST,PUT');
  res.setHeader(
    'Access-Control-Allow-Headers',
    'X-CSRF-Token, X-Requested-With, Accept, Accept-Version, Content-Length, Content-MD5, Content-Type, Date, X-Api-Version'
  );

  if (req.method === 'OPTIONS') {
    return res.status(200).end();
  }

  if (req.method !== 'POST') {
    console.log('Method not allowed:', req.method);
    return res.status(405).json({ message: 'Method not allowed' });
  }

  try {
    const { username, password } = req.body;
    console.log('Login credentials received:', { username, password: '***' });

    if (!username || !password) {
      return res.status(400).json({
        success: false,
        message: 'Username and password are required'
      });
    }

    // Query user from Supabase
    const { data: users, error } = await supabase
      .from('users')
      .select('*')
      .eq('username', username)
      .single();

    if (error) {
      console.error('Supabase query error:', error);
      return res.status(500).json({
        success: false,
        message: 'Database error',
        error: error.message
      });
    }

    if (!users) {
      console.log('User not found:', username);
      return res.status(401).json({
        success: false,
        message: 'Invalid username or password'
      });
    }

    // Verify password
    const isValidPassword = await compare(password, users.password);
    if (!isValidPassword) {
      console.log('Invalid password for user:', username);
      return res.status(401).json({
        success: false,
        message: 'Invalid username or password'
      });
    }

    console.log('Login successful for user:', username);
    return res.status(200).json({
      success: true,
      message: 'Login successful',
      user: {
        id: users.id,
        username: users.username,
        role: users.role,
        is_admin: users.is_admin
      }
    });

  } catch (error) {
    console.error('Login error:', error);
    return res.status(500).json({
      success: false,
      message: 'Internal server error',
      error: error.message
    });
  }
} 