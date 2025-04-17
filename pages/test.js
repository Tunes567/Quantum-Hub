export default function Test() {
  return (
    <div style={{ 
      padding: '2rem', 
      maxWidth: '600px', 
      margin: '0 auto',
      fontFamily: 'system-ui, sans-serif'
    }}>
      <h1>Test Page</h1>
      <p>If you can see this page, Next.js is working correctly.</p>
      <p>Deployment timestamp: {new Date().toISOString()}</p>
    </div>
  )
} 