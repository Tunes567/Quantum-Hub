import { createClient } from '@supabase/supabase-js';
import { compare } from 'bcryptjs';

export default async function handler(req, res) {
  // Set CORS headers
  res.setHeader('Access-Control-Allow-Credentials', true);
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'POST,OPTIONS');
  res.setHeader(
    'Access-Control-Allow-Headers',
    'X-CSRF-Token, X-Requested-With, Accept, Accept-Version, Content-Length, Content-MD5, Content-Type, Date, X-Api-Version'
  );

  // Handle OPTIONS request
  if (req.method === 'OPTIONS') {
    return res.status(200).json({ message: 'CORS preflight response' });
  }

  // Only allow POST requests
  if (req.method !== 'POST') {
    return res.status(405).json({ 
      success: false,
      message: 'Method not allowed',
      allowedMethods: ['POST']
    });
  }

  try {
    // Log request details for debugging
    console.log('Debug login API hit:', {
      method: req.method,
      contentType: req.headers['content-type'],
      hasBody: !!req.body
    });

    // Get environment variables
    const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL || process.env.SUPABASE_URL;
    const supabaseKey = process.env.SUPABASE_KEY;
    
    // Check if Supabase credentials are available
    if (!supabaseUrl || !supabaseKey) {
      return res.status(500).json({
        success: false,
        message: 'Server configuration error: Missing Supabase credentials',
        debug: {
          supabaseUrlSet: !!supabaseUrl,
          supabaseKeySet: !!supabaseKey,
          env: process.env.NODE_ENV
        }
      });
    }
    
    // Extract credentials from request body
    const { username, password } = req.body || {};
    
    if (!username || !password) {
      return res.status(400).json({
        success: false,
        message: 'Username and password are required',
        received: {
          username: !!username,
          password: !!password
        }
      });
    }

    // Initialize Supabase client
    const supabase = createClient(supabaseUrl, supabaseKey);
    
    // Query user from Supabase
    const { data: users, error } = await supabase
      .from('users')
      .select('*')
      .eq('username', username)
      .single();

    if (error) {
      return res.status(500).json({
        success: false,
        message: 'Database error',
        error: error.message,
        code: error.code
      });
    }

    if (!users) {
      return res.status(401).json({
        success: false,
        message: 'Invalid username or password'
      });
    }

    // Verify password
    let isValidPassword;
    try {
      isValidPassword = await compare(password, users.password);
    } catch (passwordError) {
      return res.status(500).json({
        success: false,
        message: 'Error validating credentials',
        error: passwordError.message
      });
    }
    
    if (!isValidPassword) {
      return res.status(401).json({
        success: false,
        message: 'Invalid username or password'
      });
    }

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
    return res.status(500).json({
      success: false,
      message: 'Internal server error',
      error: error.message
    });
  }
} 