import Head from 'next/head';
import { useState, useEffect } from 'react';
import { useRouter } from 'next/router';

export default function Dashboard() {
  const [stats, setStats] = useState({
    systemBalance: 0,
    totalUsers: 0,
    messagesSent: 0,
    totalRevenue: 0
  });
  const [users, setUsers] = useState([]);
  const router = useRouter();

  useEffect(() => {
    // Fetch dashboard data
    const fetchDashboardData = async () => {
      try {
        const response = await fetch('/api/admin/dashboard');
        const data = await response.json();
        setStats(data.stats);
        setUsers(data.users);
      } catch (error) {
        console.error('Error fetching dashboard data:', error);
      }
    };

    fetchDashboardData();
  }, []);

  return (
    <>
      <Head>
        <title>Admin Dashboard - Quantum Hub SMS</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet" />
        <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet" />
      </Head>

      <div className="container-fluid">
        <div className="row">
          {/* Sidebar */}
          <div className="col-md-3 col-lg-2 sidebar">
            <h3 className="mb-4">Quantum Hub SMS</h3>
            <nav className="nav flex-column">
              <a className="nav-link active" href="#dashboard">
                <i className="fas fa-tachometer-alt me-2"></i> Dashboard
              </a>
              <a className="nav-link" href="#users">
                <i className="fas fa-users me-2"></i> Users
              </a>
              <a className="nav-link" href="#messages">
                <i className="fas fa-envelope me-2"></i> Messages
              </a>
              <a className="nav-link" href="#settings">
                <i className="fas fa-cog me-2"></i> Settings
              </a>
              <a className="nav-link" href="/api/auth/logout">
                <i className="fas fa-sign-out-alt me-2"></i> Logout
              </a>
            </nav>
          </div>

          {/* Main Content */}
          <div className="col-md-9 col-lg-10 main-content">
            <h2 className="mb-4">Admin Dashboard</h2>
            
            {/* Quick Stats */}
            <div className="row mb-4">
              <div className="col-md-3">
                <div className="card stat-card">
                  <div className="d-flex justify-content-between align-items-center">
                    <div>
                      <h6>System Balance</h6>
                      <h3>€{stats.systemBalance.toFixed(2)}</h3>
                    </div>
                    <i className="fas fa-wallet"></i>
                  </div>
                </div>
              </div>
              <div className="col-md-3">
                <div className="card stat-card">
                  <div className="d-flex justify-content-between align-items-center">
                    <div>
                      <h6>Total Users</h6>
                      <h3>{stats.totalUsers}</h3>
                    </div>
                    <i className="fas fa-users"></i>
                  </div>
                </div>
              </div>
              <div className="col-md-3">
                <div className="card stat-card">
                  <div className="d-flex justify-content-between align-items-center">
                    <div>
                      <h6>Messages Sent</h6>
                      <h3>{stats.messagesSent}</h3>
                    </div>
                    <i className="fas fa-paper-plane"></i>
                  </div>
                </div>
              </div>
              <div className="col-md-3">
                <div className="card stat-card">
                  <div className="d-flex justify-content-between align-items-center">
                    <div>
                      <h6>Total Revenue</h6>
                      <h3>€{stats.totalRevenue.toFixed(2)}</h3>
                    </div>
                    <i className="fas fa-chart-line"></i>
                  </div>
                </div>
              </div>
            </div>

            {/* Quick Actions */}
            <div className="card mb-4">
              <div className="card-body">
                <h5 className="card-title mb-4">Quick Actions</h5>
                <div className="quick-actions">
                  <button className="btn btn-primary me-2" onClick={() => router.push('/admin/send-sms')}>
                    <i className="fas fa-paper-plane me-2"></i>Send SMS
                  </button>
                  <button className="btn btn-primary me-2" onClick={() => router.push('/admin/create-user')}>
                    <i className="fas fa-user-plus me-2"></i>Create User
                  </button>
                  <button className="btn btn-primary me-2" onClick={() => router.push('/admin/add-credits')}>
                    <i className="fas fa-plus-circle me-2"></i>Add System Credits
                  </button>
                  <button className="btn btn-primary" onClick={() => router.push('/admin/settings')}>
                    <i className="fas fa-cog me-2"></i>System Settings
                  </button>
                </div>
              </div>
            </div>

            {/* User Management */}
            <div className="card">
              <div className="card-header d-flex justify-content-between align-items-center">
                <h5 className="mb-0">User Management</h5>
                <button className="btn btn-sm btn-primary" onClick={() => router.push('/admin/create-user')}>
                  <i className="fas fa-plus me-1"></i>Add User
                </button>
              </div>
              <div className="card-body p-0">
                <div className="table-responsive">
                  <table className="table table-hover mb-0">
                    <thead>
                      <tr>
                        <th>Username</th>
                        <th>Email</th>
                        <th>Credits</th>
                        <th>SMS Rate</th>
                        <th>Status</th>
                        <th>Actions</th>
                      </tr>
                    </thead>
                    <tbody>
                      {users.map((user) => (
                        <tr key={user.id}>
                          <td>{user.username}</td>
                          <td>{user.email}</td>
                          <td>€{user.credits.toFixed(2)}</td>
                          <td>€{user.smsRate.toFixed(2)}</td>
                          <td>
                            <span className={`badge bg-${user.active ? 'success' : 'danger'}`}>
                              {user.active ? 'Active' : 'Inactive'}
                            </span>
                          </td>
                          <td>
                            <button className="btn btn-sm btn-primary me-1" onClick={() => router.push(`/admin/users/${user.id}`)}>
                              <i className="fas fa-edit"></i>
                            </button>
                            <button className="btn btn-sm btn-danger">
                              <i className="fas fa-trash"></i>
                            </button>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <style jsx>{`
        :root {
          --primary-color: #2c3e50;
          --secondary-color: #3498db;
          --accent-color: #e74c3c;
          --light-bg: #f8f9fa;
          --success-color: #2ecc71;
          --warning-color: #f1c40f;
        }
        
        .sidebar {
          background-color: var(--primary-color);
          min-height: 100vh;
          padding: 20px;
          color: white;
        }
        
        .sidebar .nav-link {
          color: rgba(255, 255, 255, 0.8);
          margin: 5px 0;
          border-radius: 5px;
          transition: all 0.3s;
          padding: 10px 15px;
        }
        
        .sidebar .nav-link:hover {
          background-color: var(--secondary-color);
          color: white;
        }
        
        .sidebar .nav-link.active {
          background-color: var(--secondary-color);
          color: white;
        }
        
        .main-content {
          padding: 20px;
          background-color: var(--light-bg);
        }
        
        .card {
          border: none;
          border-radius: 10px;
          box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
          margin-bottom: 20px;
          transition: transform 0.3s;
        }
        
        .stat-card {
          background: linear-gradient(45deg, var(--primary-color), var(--secondary-color));
          color: white;
          padding: 20px;
        }
        
        .stat-card i {
          font-size: 2.5rem;
          opacity: 0.8;
        }

        .stat-card h6 {
          font-size: 0.9rem;
          opacity: 0.8;
          margin-bottom: 5px;
        }

        .stat-card h3 {
          font-size: 1.8rem;
          margin-bottom: 0;
        }
        
        .quick-actions .btn {
          padding: 15px 25px;
          border-radius: 8px;
          transition: all 0.3s;
        }

        .quick-actions .btn i {
          font-size: 1.2rem;
        }

        .table th {
          font-weight: 600;
          color: var(--primary-color);
        }

        .table td {
          vertical-align: middle;
        }

        .badge {
          padding: 6px 12px;
          font-weight: 500;
        }
      `}</style>
    </>
  );
} 