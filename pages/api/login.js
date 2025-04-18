import { createClient } from '@supabase/supabase-js';
import { compare } from 'bcryptjs';

export default async function handler(req, res) {
  console.log('API Route Hit:', req.method);
  console.log('Environment check:', {
    supabaseUrl: process.env.NEXT_PUBLIC_SUPABASE_URL ? 'Set' : 'Not Set',
    supabaseKey: process.env.SUPABASE_KEY ? 'Set' : 'Not Set',
    nodeEnv: process.env.NODE_ENV
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
    // Check if Supabase credentials are available
    if (!process.env.NEXT_PUBLIC_SUPABASE_URL || !process.env.SUPABASE_KEY) {
      console.error('Supabase credentials missing');
      return res.status(500).json({
        success: false,
        message: 'Server configuration error: Missing Supabase credentials',
        debug: {
          supabaseUrlSet: !!process.env.NEXT_PUBLIC_SUPABASE_URL,
          supabaseKeySet: !!process.env.SUPABASE_KEY,
          env: process.env.NODE_ENV
        }
      });
    }
    
    // Initialize Supabase client
    let supabase;
    try {
      supabase = createClient(
        process.env.NEXT_PUBLIC_SUPABASE_URL,
        process.env.SUPABASE_KEY
      );
      console.log('Supabase client initialized');
    } catch (initError) {
      console.error('Supabase client initialization error:', initError);
      return res.status(500).json({
        success: false,
        message: 'Server error: Could not initialize database client',
        error: initError.message
      });
    }

    const { username, password } = req.body;
    console.log('Login credentials received:', { username, password: '***' });

    if (!username || !password) {
      return res.status(400).json({
        success: false,
        message: 'Username and password are required'
      });
    }

    // Query user from Supabase
    let queryResponse;
    try {
      queryResponse = await supabase
        .from('users')
        .select('*')
        .eq('username', username)
        .single();
      
      console.log('Query response:', {
        hasError: !!queryResponse.error,
        errorMessage: queryResponse.error?.message,
        hasData: !!queryResponse.data
      });
    } catch (queryError) {
      console.error('Unexpected query error:', queryError);
      return res.status(500).json({
        success: false,
        message: 'Database query error',
        error: queryError.message
      });
    }

    const { data: users, error } = queryResponse;

    if (error) {
      console.error('Supabase query error:', error);
      
      // Check for "not found" errors vs other errors
      if (error.code === 'PGRST116') {
        return res.status(401).json({
          success: false,
          message: 'Invalid username or password'
        });
      }
      
      return res.status(500).json({
        success: false,
        message: 'Database error',
        error: error.message,
        code: error.code
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
    let isValidPassword;
    try {
      isValidPassword = await compare(password, users.password);
      console.log('Password validation result:', isValidPassword);
    } catch (passwordError) {
      console.error('Password comparison error:', passwordError);
      return res.status(500).json({
        success: false,
        message: 'Error validating credentials',
        error: passwordError.message
      });
    }
    
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
      error: error.message,
      stack: process.env.NODE_ENV === 'development' ? error.stack : undefined
    });
  }
} 