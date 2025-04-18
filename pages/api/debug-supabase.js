import { createClient } from '@supabase/supabase-js';

export default async function handler(req, res) {
  // Set CORS headers
  res.setHeader('Access-Control-Allow-Credentials', true);
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET,OPTIONS');
  res.setHeader(
    'Access-Control-Allow-Headers',
    'X-CSRF-Token, X-Requested-With, Accept, Accept-Version, Content-Length, Content-MD5, Content-Type, Date, X-Api-Version'
  );

  if (req.method === 'OPTIONS') {
    return res.status(200).end();
  }

  try {
    // Check environment variables
    const envInfo = {
      supabaseUrlSet: !!process.env.NEXT_PUBLIC_SUPABASE_URL,
      supabaseKeySet: !!process.env.SUPABASE_KEY,
      supabaseUrl: process.env.NEXT_PUBLIC_SUPABASE_URL?.substring(0, 10) + '...',
      nodeEnv: process.env.NODE_ENV,
    };

    // Attempt to initialize Supabase client
    let supabaseInfo = { initialized: false };
    try {
      const supabase = createClient(
        process.env.NEXT_PUBLIC_SUPABASE_URL,
        process.env.SUPABASE_KEY
      );
      
      supabaseInfo.initialized = true;
      
      // Test a basic query
      const { data, error } = await supabase
        .from('users')
        .select('count(*)');
      
      supabaseInfo.querySucceeded = !error;
      supabaseInfo.errorMessage = error ? error.message : null;
      supabaseInfo.data = data;
      
    } catch (supabaseError) {
      supabaseInfo.error = supabaseError.message;
    }

    return res.status(200).json({
      message: 'Debugging information',
      environment: envInfo,
      supabase: supabaseInfo,
      timestamp: new Date().toISOString()
    });
  } catch (error) {
    return res.status(500).json({
      message: 'Error in debug endpoint',
      error: error.message
    });
  }
} 