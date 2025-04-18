import { verify } from 'jsonwebtoken';
import { compare } from 'bcryptjs';
import sqlite3 from 'sqlite3';
import { open } from 'sqlite';

// Initialize database connection
async function openDb() {
  return open({
    filename: './users.db',
    driver: sqlite3.Database
  });
}

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

    // For testing, accept any login with non-empty values
    if (username && password) {
      console.log('Login successful for user:', username);
      return res.status(200).json({
        success: true,
        message: 'Login successful',
        user: {
          id: 1,
          username: username,
          role: 'user'
        }
      });
    } else {
      console.log('Login failed: Missing credentials');
      return res.status(400).json({ 
        success: false,
        message: 'Username and password are required' 
      });
    }

  } catch (error) {
    console.error('Login error:', error);
    return res.status(500).json({ 
      success: false,
      message: 'Internal server error',
      error: error.message 
    });
  }
} 