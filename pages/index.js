import { useState, useEffect } from 'react'
import Head from 'next/head'

export default function Home() {
  const [status, setStatus] = useState('Loading...');
  const [errorDetails, setErrorDetails] = useState('');
  
  useEffect(() => {
    const checkAPI = async () => {
      try {
        // Try Next.js API route first
        const res = await fetch('/api/health');
        
        if (!res.ok) {
          throw new Error(`HTTP error! Status: ${res.status}`);
        }
        
        const data = await res.json();
        setStatus(data.status);
        setErrorDetails('');
      } catch (err) {
        console.error('API Error:', err);
        setStatus('Error connecting to API');
        setErrorDetails(`${err.message}`);
        
        // Try alternative API endpoint as backup
        try {
          const fallbackRes = await fetch('/api/hello');
          if (fallbackRes.ok) {
            const fallbackData = await fallbackRes.json();
            setErrorDetails(prev => `${prev} (Fallback API is working: ${fallbackData.message})`);
          }
        } catch (fallbackErr) {
          console.error('Fallback API Error:', fallbackErr);
        }
      }
    };
    
    checkAPI();
  }, []);

  return (
    <>
      <Head>
        <title>Quantum Hub SMS</title>
        <meta name="description" content="SMS messaging platform" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <link rel="icon" href="/favicon.ico" />
      </Head>
      <main style={{ 
        padding: '2rem',
        maxWidth: '800px',
        margin: '0 auto',
        fontFamily: 'Arial, sans-serif'
      }}>
        <h1 style={{ color: '#333' }}>Quantum Hub SMS</h1>
        
        <div style={{ 
          border: '1px solid #ddd',
          borderRadius: '8px',
          padding: '2rem',
          marginTop: '2rem',
          backgroundColor: '#f9f9f9'
        }}>
          <h2 style={{ color: '#0070f3' }}>System Status</h2>
          <p>API Status: <span style={{ 
            fontWeight: 'bold',
            color: status === 'healthy' ? 'green' : 'red'
          }}>{status}</span></p>
          
          {errorDetails && (
            <div style={{ 
              marginTop: '1rem', 
              padding: '0.5rem', 
              backgroundColor: 'rgba(255,0,0,0.05)', 
              borderRadius: '4px',
              fontSize: '0.8rem',
              color: '#666'
            }}>
              {errorDetails}
            </div>
          )}
          
          <div style={{ marginTop: '2rem' }}>
            <h3>Quick Links</h3>
            <ul>
              <li><a href="/api/hello" style={{ color: '#0070f3' }}>API Test Endpoint</a></li>
              <li><a href="/api/health" style={{ color: '#0070f3' }}>API Health Check</a></li>
            </ul>
          </div>
        </div>
      </main>
    </>
  )
} 