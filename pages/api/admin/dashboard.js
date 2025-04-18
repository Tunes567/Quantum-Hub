import { getSession } from 'next-auth/react';
import prisma from '../../../lib/prisma';

export default async function handler(req, res) {
  if (req.method !== 'GET') {
    return res.status(405).json({ message: 'Method not allowed' });
  }

  try {
    const session = await getSession({ req });
    
    if (!session || !session.user.isAdmin) {
      return res.status(401).json({ message: 'Unauthorized' });
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

    return res.status(200).json({
      totalUsers,
      messagesSent,
      totalRevenue: totalRevenue._sum.amount || 0,
      systemBalance: systemBalance?.balance || 0,
      recentUsers
    });
  } catch (error) {
    console.error('Dashboard API Error:', error);
    return res.status(500).json({ message: 'Internal server error' });
  }
} 