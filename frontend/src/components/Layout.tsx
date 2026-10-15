import { Outlet, NavLink, useNavigate } from 'react-router-dom'
import { useState, useEffect } from 'react'
import { getHealth } from '../api/client'

function Layout() {
  const navigate = useNavigate()
  const [health, setHealth] = useState<{ status: string; version: string } | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    getHealth()
      .then(setHealth)
      .catch(() => setHealth({ status: 'error', version: 'unknown' }))
      .finally(() => setLoading(false))
  }, [])

  const handleLogout = () => {
    sessionStorage.clear()
    navigate('/login')
  }

  const navItems = [
    { path: '/', label: 'Dashboard' },
    { path: '/skills', label: 'Skills' },
    { path: '/genetics', label: 'Genetics' },
    { path: '/onboarding', label: 'Onboarding' },
  ]

  return (
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
      <header style={{
        background: 'var(--color-surface)',
        borderBottom: '1px solid var(--color-border)',
        padding: '1rem 1.5rem',
        position: 'sticky',
        top: 0,
        zIndex: 100,
      }}>
        <div className="container" style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '1rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
            <h1 style={{ fontSize: '1.25rem', fontWeight: 600, color: 'var(--color-primary)' }}>
              Atlas Lab
            </h1>
            <span className={`badge ${health?.status === 'ok' ? 'badge-success' : 'badge-error'}`}>
              {loading ? 'Loading...' : health?.status === 'ok' ? 'API Connected' : 'API Disconnected'}
            </span>
          </div>
          <nav style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            {navItems.map((item) => (
              <NavLink
                key={item.path}
                to={item.path}
                style={({ isActive }) => ({
                  padding: '0.5rem 1rem',
                  borderRadius: 'var(--radius-md)',
                  fontWeight: 500,
                  color: isActive ? 'var(--color-primary)' : 'var(--color-text)',
                  background: isActive ? 'rgb(37 99 235 / 0.1)' : 'transparent',
                  textDecoration: 'none',
                })}
              >
                {item.label}
              </NavLink>
            ))}
            <button
              onClick={handleLogout}
              className="btn btn-secondary"
              style={{ marginLeft: '1rem' }}
            >
              Logout
            </button>
          </nav>
        </div>
      </header>
      <main style={{ flex: 1, padding: '2rem 0' }}>
        <div className="container">
          <Outlet />
        </div>
      </main>
      <footer style={{
        background: 'var(--color-surface)',
        borderTop: '1px solid var(--color-border)',
        padding: '1.5rem',
        marginTop: 'auto',
      }}>
        <div className="container" style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '1rem', fontSize: '0.875rem', color: 'var(--color-text-muted)' }}>
          <span>Atlas Lab v1.0.0 \u2014 Alan Vo \u2014 alanvo@gmail.com</span>
          <span>AI/ML Developer Tools for Scientific Research</span>
        </div>
      </footer>
    </div>
  )
}

export default Layout