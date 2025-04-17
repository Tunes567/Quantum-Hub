export default function handler(req, res) {
  res.status(200).json({
    status: 'healthy',
    message: 'API is operational',
    timestamp: new Date().toISOString()
  })
} 