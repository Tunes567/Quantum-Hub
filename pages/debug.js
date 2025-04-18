import { useState, useEffect } from 'react';
import Head from 'next/head';

export default function DebugPage() {
  const [username, setUsername] = useState('admin');
  const [password, setPassword] = useState('admin123');
  const [loginResponse, setLoginResponse] = useState(null);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [supabaseInfo, setSupabaseInfo] = useState(null);
  const [supabaseLoading, setSupabaseLoading] = useState(false);

  // Function to test login
  const testLogin = async () => {
    setLoading(true);
    setError('');
    setLoginResponse(null);
    
    try {
      const response = await fetch('/api/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ username, password }),
      });
      
      const data = await response.json();
      setLoginResponse({
        status: response.status,
        ok: response.ok,
        data
      });
    } catch (err) {
      setError(`Error: ${err.message}`);
      console.error('Login test error:', err);
    } finally {
      setLoading(false);
    }
  };

  // Function to check Supabase connection
  const checkSupabase = async () => {
    setSupabaseLoading(true);
    try {
      const response = await fetch('/api/debug-supabase');
      const data = await response.json();
      setSupabaseInfo(data);
    } catch (err) {
      console.error('Supabase check error:', err);
      setSupabaseInfo({ error: err.message });
    } finally {
      setSupabaseLoading(false);
    }
  };

  return (
    <div>
      <Head>
        <title>API Debug Page</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet" />
      </Head>

      <div className="container mt-5">
        <h1>API Debugging</h1>
        
        <div className="card mb-4">
          <div className="card-header bg-primary text-white">
            <h4>Supabase Connection Test</h4>
          </div>
          <div className="card-body">
            <button 
              className="btn btn-primary mb-3" 
              onClick={checkSupabase}
              disabled={supabaseLoading}
            >
              {supabaseLoading ? 'Checking...' : 'Check Supabase Connection'}
            </button>
            
            {supabaseInfo && (
              <div className="mt-3">
                <h5>Results:</h5>
                <pre className="bg-light p-3 border rounded">
                  {JSON.stringify(supabaseInfo, null, 2)}
                </pre>
              </div>
            )}
          </div>
        </div>
        
        <div className="card">
          <div className="card-header bg-primary text-white">
            <h4>Login Test</h4>
          </div>
          <div className="card-body">
            <div className="mb-3">
              <label htmlFor="username" className="form-label">Username</label>
              <input 
                type="text" 
                className="form-control" 
                id="username"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
              />
            </div>
            
            <div className="mb-3">
              <label htmlFor="password" className="form-label">Password</label>
              <input 
                type="password" 
                className="form-control" 
                id="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
              />
            </div>
            
            <button 
              className="btn btn-primary" 
              onClick={testLogin}
              disabled={loading}
            >
              {loading ? 'Testing...' : 'Test Login'}
            </button>
            
            {error && (
              <div className="alert alert-danger mt-3">
                {error}
              </div>
            )}
            
            {loginResponse && (
              <div className="mt-3">
                <h5>Login Response:</h5>
                <p>Status: {loginResponse.status} ({loginResponse.ok ? 'Success' : 'Failed'})</p>
                <pre className="bg-light p-3 border rounded">
                  {JSON.stringify(loginResponse.data, null, 2)}
                </pre>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
} 