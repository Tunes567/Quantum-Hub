import { getSession } from 'next-auth/react';
import prisma from '../../../lib/prisma';

export default async function handler(req, res) {
  // Set CORS headers
  res.setHeader('Access-Control-Allow-Credentials', true);
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET,OPTIONS');
  res.setHeader(
    'Access-Control-Allow-Headers',
    'X-CSRF-Token, X-Requested-With, Accept, Accept-Version, Content-Length, Content-MD5, Content-Type, Date, X-Api-Version'
  );

  // Handle OPTIONS request
  if (req.method === 'OPTIONS') {
    res.status(200).end();
    return;
  }

  // Only allow GET requests
  if (req.method !== 'GET') {
    return res.status(405).json({ 
      message: 'Method not allowed',
      allowedMethods: ['GET']
    });
  }

  try {
    const session = await getSession({ req });
    
    if (!session) {
      return res.status(401).json({ message: 'Not authenticated' });
    }

    if (!session.user.isAdmin) {
      return res.status(403).json({ message: 'Not authorized' });
    }

    // Fetch dashboard statistics
    const [
      totalUsers,
      messagesSent,
      totalRevenue,
      systemBalance,
      recentUsers
    ] = await Promise.all([
      prisma.user.count(),
      prisma.message.count(),
      prisma.payment.aggregate({
        _sum: {
          amount: true
        }
      }),
      prisma.systemBalance.findFirst({
        orderBy: {
          updatedAt: 'desc'
        }
      }),
      prisma.user.findMany({
        take: 5,
        orderBy: {
          createdAt: 'desc'
        },
        select: {
          id: true,
          name: true,
          email: true,
          createdAt: true,
          isActive: true
        }
      })
    ]);

    // Format the response
    const response = {
      stats: {
        totalUsers,
        messagesSent,
        totalRevenue: totalRevenue._sum.amount || 0,
        systemBalance: systemBalance?.balance || 0
      },
      recentUsers
    };

    return res.status(200).json(response);
  } catch (error) {
    console.error('Error in dashboard API:', error);
    return res.status(500).json({ 
      message: 'Internal server error',
      error: error.message 
    });
  }
} 