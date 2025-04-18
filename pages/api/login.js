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
  if (req.method !== 'POST') {
    return res.status(405).json({ message: 'Method not allowed' });
  }

  try {
    const { username, password } = req.body;
    console.log('Login attempt:', { username }); // Log the attempt

    // For testing, accept any login
    if (username && password) {
      return res.status(200).json({
        message: 'Login successful',
        user: {
          id: 1,
          username: username,
          role: 'user'
        }
      });
    } else {
      return res.status(400).json({ message: 'Username and password are required' });
    }

  } catch (error) {
    console.error('Login error:', error);
    return res.status(500).json({ message: 'Internal server error' });
  }
} 