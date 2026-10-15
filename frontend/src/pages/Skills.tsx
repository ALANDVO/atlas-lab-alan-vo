import { useEffect, useState } from 'react'
import { Skill, listSkills } from '../api/client'

function Skills() {
  const [skills, setSkills] = useState<Skill[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    listSkills()
      .then(setSkills)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false))
  }, [])

  return (
    <div>
      <header style={{ marginBottom: '2rem' }}>
        <h2 style={{ fontSize: '1.75rem', fontWeight: 600, marginBottom: '0.5rem' }}>Skill Registry</h2>
        <p style={{ color: 'var(--color-text-muted)' }}>Browse and manage validated agent skills for scientific workflows.</p>
      </header>

      {loading ? (
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: '200px' }}>
          <div className="loading" style={{ width: '2rem', height: '2rem' }} />
        </div>
      ) : error ? (
        <div className="card" style={{ borderColor: 'var(--color-error)', color: 'var(--color-error)' }}>
          Failed to load skills: {error}
        </div>
      ) : skills.length === 0 ? (
        <div className="empty-state">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
            <path d="M12 4v16m8-8H4" />
            <path d="M8 8h8m-8 4h8m-8 4h8" />
          </svg>
          <h3>No skills yet</h3>
          <p>Skills will appear here once the registry is implemented.</p>
        </div>
      ) : (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(320px, 1fr))', gap: '1rem' }}>
          {skills.map((skill) => (
            <div key={skill.id} className="card">
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '0.5rem' }}>
                <h3 style={{ fontSize: '1.125rem', fontWeight: 600 }}>{skill.name}</h3>
                <span className="badge badge-info">{skill.category}</span>
              </div>
              <p style={{ color: 'var(--color-text-muted)', fontSize: '0.875rem', marginBottom: '0.75rem' }}>{skill.description}</p>
              <div style={{ display: 'flex', gap: '1rem', fontSize: '0.75rem', color: 'var(--color-text-muted)' }}>
                <span>v{skill.version}</span>
                <span>by {skill.author}</span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

export default Skills