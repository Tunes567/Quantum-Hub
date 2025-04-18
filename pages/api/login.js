import { createClient } from '@supabase/supabase-js';
import { compare } from 'bcryptjs';

// Initialize Supabase client
const supabase = createClient(
  process.env.SUPABASE_URL,
  process.env.SUPABASE_KEY
);

export default async function handler(req, res) {
  console.log('API Route Hit:', req.method);
  console.log('Request body:', req.body);

  if (req.method !== 'POST') {
    console.log('Method not allowed:', req.method);
    return res.status(405).json({ message: 'Method not allowed' });
  }

  try {
    const { username, password } = req.body;
    console.log('Login credentials received:', { username, password: '***' });

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
        message: 'Database error'
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