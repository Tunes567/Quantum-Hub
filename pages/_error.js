function Error({ statusCode }) {
  return (
    <div style={{
      padding: '2rem',
      maxWidth: '600px',
      margin: '0 auto',
      fontFamily: 'system-ui, sans-serif',
      textAlign: 'center'
    }}>
      <h1>Error</h1>
      <p>
        {statusCode
          ? `A ${statusCode} error occurred on the server`
          : 'An error occurred on the client'}
      </p>
      <p>
        <a href="/" style={{ color: '#0070f3', textDecoration: 'underline' }}>
          Go back to the homepage
        </a>
      </p>
    </div>
  )
}

Error.getInitialProps = ({ res, err }) => {
  const statusCode = res ? res.statusCode : err ? err.statusCode : 404
  return { statusCode }
}

export default Error 