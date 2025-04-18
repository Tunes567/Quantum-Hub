import Head from 'next/head';

export default function Dashboard() {
  return (
    <>
      <Head>
        <title>Dashboard - Quantum Hub SMS</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet" />
        <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet" />
      </Head>

      <div className="container mt-5">
        <div className="row">
          <div className="col-12">
            <h1 className="mb-4">Welcome to Your Dashboard</h1>
            <div className="card">
              <div className="card-body">
                <h5 className="card-title">Quick Stats</h5>
                <div className="row mt-4">
                  <div className="col-md-4">
                    <div className="card bg-primary text-white">
                      <div className="card-body">
                        <h6 className="card-subtitle mb-2">Messages Sent</h6>
                        <h2 className="card-title mb-0">0</h2>
                      </div>
                    </div>
                  </div>
                  <div className="col-md-4">
                    <div className="card bg-success text-white">
                      <div className="card-body">
                        <h6 className="card-subtitle mb-2">Delivery Rate</h6>
                        <h2 className="card-title mb-0">0%</h2>
                      </div>
                    </div>
                  </div>
                  <div className="col-md-4">
                    <div className="card bg-info text-white">
                      <div className="card-body">
                        <h6 className="card-subtitle mb-2">Credits</h6>
                        <h2 className="card-title mb-0">0</h2>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </>
  );
} 