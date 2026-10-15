import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { getHealth, getDbHealth } from '../api/client'

function Dashboard() {
  const [health, setHealth] = useState<{ status: string; app: string; version: string; environment: string } | null>(null)
  const [dbHealth, setDbHealth] = useState<{ status: string; database: string; error?: string } | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    Promise.all([getHealth(), getDbHealth()])
      .then(([h, db]) => {
        setHealth(h)
        setDbHealth(db)
      })
      .catch(() => {})
      .finally(() => setLoading(false))
  }, [])

  const workflows = [
    {
      title: 'Statistical Genetics: Locus Compare',
      description: 'Fetch GWAS/eQTL data, compute LD from 1000 Genomes, and render 4-panel locus compare plots for colocalization analysis.',
      path: '/genetics',
      icon: '🧬',
      status: 'coming-soon',
    },
    {
      title: 'Field Onboarding',
      description: 'Step-by-step orientation in unfamiliar research fields: prerequisite assessment, ladder teaching, and passage decoding.',
      path: '/onboarding',
      icon: '📚',
      status: 'coming-soon',
    },
    {
      title: 'Skill Registry',
      description: 'Browse, search, and manage validated agent skills for scientific workflows.',
      path: '/skills',
      icon: '🛠️',
      status: 'coming-soon',
    },
  ]

  if (loading) {
    return (
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: '300px' }}>
        <div className="loading" style={{ width: '2rem', height: '2rem' }} role="status" aria-label="Loading" />
      </div>
    )
  }

  return (
    <div>
      <section style={{ marginBottom: '2rem' }}>
        <h2 style={{ fontSize: '1.75rem', fontWeight: 600, marginBottom: '0.5rem' }}>Dashboard</h2>
        <p style={{ color: 'var(--color-text-muted)' }}>
          Welcome to Atlas Lab. Turn any AI agent into an AI Scientist with validated skills for biology, chemistry, medicine, and drug discovery.
        </p>
      </section>

      <section style={{ marginBottom: '2rem' }}>
        <h3 style={{ fontSize: '1.125rem', fontWeight: 600, marginBottom: '1rem' }}>System Health</h3>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem' }}>
          <div className="card">
            <div style={{ fontSize: '0.875rem', color: 'var(--color-text-muted)', marginBottom: '0.25rem' }}>API Status</div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <span className={`badge ${health?.status === 'ok' ? 'badge-success' : 'badge-error'}`}>
                {health?.status === 'ok' ? 'Healthy' : 'Unhealthy'}
              </span>
              <span style={{ fontSize: '0.875rem', color: 'var(--color-text-muted)' }}>
                v{health?.version ?? 'unknown'}
              </span>
            </div>
          </div>
          <div className="card">
            <div style={{ fontSize: '0.875rem', color: 'var(--color-text-muted)', marginBottom: '0.25rem' }}>Database</div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <span className={`badge ${dbHealth?.status === 'ok' ? 'badge-success' : 'badge-error'}`}>
                {dbHealth?.database === 'connected' ? 'Connected' : 'Disconnected'}
              </span>
              {dbHealth?.error && <span style={{ fontSize: '0.75rem', color: 'var(--color-error)' }}>{dbHealth.error}</span>}
            </div>
          </div>
          <div className="card">
            <div style={{ fontSize: '0.875rem', color: 'var(--color-text-muted)', marginBottom: '0.25rem' }}>Environment</div>
            <div>{health?.environment ?? 'unknown'}</div>
          </div>
          <div className="card">
            <div style={{ fontSize: '0.875rem', color: 'var(--color-text-muted)', marginBottom: '0.25rem' }}>Application</div>
            <div>{health?.app ?? 'atlas-lab'}</div>
          </div>
        </div>
      </section>

      <section>
        <h3 style={{ fontSize: '1.125rem', fontWeight: 600, marginBottom: '1rem' }}>Available Workflows</h3>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '1rem' }}>
          {workflows.map((wf) => (
            <Link key={wf.path} to={wf.path} style={{ textDecoration: 'none' }}>
              <div className="card" style={{ transition: 'transform 0.15s ease, box-shadow 0.15s ease', height: '100%' }}>
                <div style={{ display: 'flex', alignItems: 'flex-start', gap: '1rem' }}>
                  <span style={{ fontSize: '2rem', lineHeight: 1 }}>{wf.icon}</span>
                  <div style={{ flex: 1 }}>
                    <h4 style={{ fontSize: '1rem', fontWeight: 600, marginBottom: '0.5rem' }}>{wf.title}</h4>
                    <p style={{ color: 'var(--color-text-muted)', fontSize: '0.875rem', marginBottom: '0.75rem' }}>{wf.description}</p>
                    <span className={`badge ${wf.status === 'coming-soon' ? 'badge-warning' : 'badge-info'}`}>
                      {wf.status === 'coming-soon' ? 'Coming Soon' : 'Available'}
                    </span>
                  </div>
                </div>
              </div>
            </Link>
          ))}
        </div>
      </section>
    </div>
  )
}

export default Dashboard