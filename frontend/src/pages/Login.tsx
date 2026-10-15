import { useEffect } from 'react'
import { useNavigate } from 'react-router-dom'

function Login() {
  const navigate = useNavigate()

  useEffect(() => {
    const token = sessionStorage.getItem('access_token')
    if (token) {
      navigate('/')
    }
  }, [navigate])

  const handleDemoLogin = () => {
    sessionStorage.setItem('access_token', 'demo-token')
    sessionStorage.setItem('refresh_token', 'demo-refresh')
    navigate('/')
  }

  return (
    <div style={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', padding: '1.5rem' }}>
      <div className="card" style={{ width: '100%', maxWidth: '400px' }}>
        <div style={{ textAlign: 'center', marginBottom: '2rem' }}>
          <h1 style={{ fontSize: '2rem', fontWeight: 700, color: 'var(--color-primary)', marginBottom: '0.5rem' }}>
            Atlas Lab
          </h1>
          <p style={{ color: 'var(--color-text-muted)' }}>AI Scientist Platform</p>
        </div>

        <div style={{ marginBottom: '1.5rem', padding: '1rem', background: 'rgb(245 158 11 / 0.1)', border: '1px solid var(--color-warning)', borderRadius: 'var(--radius-md)', fontSize: '0.875rem' }}>
          <strong>Demo Mode</strong> — OIDC/Keycloak integration not yet implemented.
          Click below to continue with a local demo session.
        </div>

        <button
          onClick={handleDemoLogin}
          className="btn btn-primary"
          style={{ width: '100%', padding: '0.875rem' }}
        >
          Continue with Demo Session
        </button>

        <div style={{ marginTop: '1.5rem', textAlign: 'center', fontSize: '0.875rem', color: 'var(--color-text-muted)' }}>
          <p>Alan Vo \u2014 alanvo@gmail.com</p>
          <p>AI/ML Developer Tools for Scientific Research</p>
        </div>
      </div>
    </div>
  )
}

export default Login