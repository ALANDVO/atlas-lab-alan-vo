import { useState } from 'react'
import {
  OnboardingAssessResponse,
  LadderStepRequest,
  LadderStepResponse,
  DecodeResponse,
  assessPrerequisites,
  ladderStep,
  decodePassage as decodePassageApi,
} from '../api/client'

type Tab = 'assess' | 'ladder' | 'decode'

function Onboarding() {
  const [activeTab, setActiveTab] = useState<Tab>('assess')
  const [assessField, setAssessField] = useState('')
  const [assessBackground, setAssessBackground] = useState('')
  const [assessResult, setAssessResult] = useState<OnboardingAssessResponse | null>(null)
  const [assessLoading, setAssessLoading] = useState(false)

  const [ladderSessionId, setLadderSessionId] = useState('')
  const [ladderRung, setLadderRung] = useState<LadderStepRequest['rung']>('motivation')
  const [ladderKnown, setLadderKnown] = useState('')
  const [ladderResult, setLadderResult] = useState<LadderStepResponse | null>(null)
  const [ladderLoading, setLadderLoading] = useState(false)

  const [decodePassageText, setDecodePassageText] = useState('')
  const [decodeContext, setDecodeContext] = useState('')
  const [decodeResult, setDecodeResult] = useState<DecodeResponse | null>(null)
  const [decodeLoading, setDecodeLoading] = useState(false)

  const handleAssess = async (e: React.FormEvent) => {
    e.preventDefault()
    setAssessLoading(true)
    try {
      const res = await assessPrerequisites({
        field: assessField,
        user_background: assessBackground.split(',').map(s => s.trim()).filter(Boolean),
      })
      setAssessResult(res)
    } catch (e: unknown) {
      console.error(e)
    } finally {
      setAssessLoading(false)
    }
  }

  const handleLadder = async (e: React.FormEvent) => {
    e.preventDefault()
    setLadderLoading(true)
    try {
      const res = await ladderStep({
        session_id: ladderSessionId || 'new',
        rung: ladderRung,
        user_known_frameworks: ladderKnown.split(',').map(s => s.trim()).filter(Boolean),
      })
      setLadderResult(res)
    } catch (e: unknown) {
      console.error(e)
    } finally {
      setLadderLoading(false)
    }
  }

  const handleDecode = async (e: React.FormEvent) => {
    e.preventDefault()
    setDecodeLoading(true)
    try {
      const res = await decodePassageApi({
        passage: decodePassageText,
        field_context: decodeContext,
      })
      setDecodeResult(res)
    } catch (e: unknown) {
      console.error(e)
    } finally {
      setDecodeLoading(false)
    }
  }

  return (
    <div>
      <header style={{ marginBottom: '2rem' }}>
        <h2 style={{ fontSize: '1.75rem', fontWeight: 600, marginBottom: '0.5rem' }}>Field Onboarding</h2>
        <p style={{ color: 'var(--color-text-muted)' }}>
          Step-by-step orientation in unfamiliar research fields: prerequisite assessment, ladder teaching, and passage decoding.
        </p>
      </header>

      <div style={{ display: 'flex', gap: '0.5rem', marginBottom: '1.5rem', borderBottom: '1px solid var(--color-border)', paddingBottom: '0.5rem' }}>
        {(['assess', 'ladder', 'decode'] as Tab[]).map((tab) => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            style={{
              padding: '0.5rem 1rem',
              border: 'none',
              background: activeTab === tab ? 'var(--color-primary)' : 'transparent',
              color: activeTab === tab ? 'white' : 'var(--color-text)',
              borderRadius: 'var(--radius-md)',
              fontWeight: 500,
              cursor: 'pointer',
            }}
          >
            {tab === 'assess' && '🔍 Assess Prerequisites'}
            {tab === 'ladder' && '🪜 Ladder Teaching'}
            {tab === 'decode' && '🔬 Decode Passage'}
          </button>
        ))}
      </div>

      {activeTab === 'assess' && (
        <section className="card">
          <h3 style={{ fontSize: '1.125rem', fontWeight: 600, marginBottom: '1.5rem' }}>Prerequisite Assessment</h3>
          <form onSubmit={handleAssess}>
            <div style={{ marginBottom: '1rem' }}>
              <label className="label" htmlFor="assess-field">Research Field</label>
              <input
                id="assess-field"
                className="input"
                type="text"
                value={assessField}
                onChange={(e) => setAssessField(e.target.value)}
                placeholder="e.g., statistical genetics, single-cell RNA-seq, causal inference"
                required
              />
            </div>
            <div style={{ marginBottom: '1rem' }}>
              <label className="label" htmlFor="assess-background">Your Background (comma-separated)</label>
              <input
                id="assess-background"
                className="input"
                type="text"
                value={assessBackground}
                onChange={(e) => setAssessBackground(e.target.value)}
                placeholder="e.g., molecular biology, Python, statistics"
              />
              <p style={{ fontSize: '0.75rem', color: 'var(--color-text-muted)', marginTop: '0.25rem' }}>
                Mark frameworks you have used / learned / are new to
              </p>
            </div>
            <button type="submit" className="btn btn-primary" disabled={assessLoading}>
              {assessLoading ? <><span className="loading" style={{ width: '1rem', height: '1rem' }} /> Assessing...</> : 'Assess Prerequisites'}
            </button>
          </form>

          {assessResult && (
            <div style={{ marginTop: '1.5rem', padding: '1rem', background: 'var(--color-bg)', borderRadius: 'var(--radius-md)' }}>
              <h4 style={{ marginBottom: '0.75rem' }}>Assessment Results</h4>
              <div style={{ marginBottom: '1rem' }}>
                <strong>Field Maturity: </strong>
                <span className={`badge ${
                  assessResult.field_maturity === 'settled' ? 'badge-success' :
                  assessResult.field_maturity === 'emerging' ? 'badge-warning' : 'badge-error'
                }`}>
                  {assessResult.field_maturity}
                </span>
              </div>
              <div>
                <strong>Prerequisite Frameworks:</strong>
                <ul style={{ marginTop: '0.5rem', marginLeft: '1.5rem' }}>
                  {assessResult.prerequisites.map((p, i) => (
                    <li key={i}>{p}</li>
                  ))}
                </ul>
              </div>
            </div>
          )}
        </section>
      )}

      {activeTab === 'ladder' && (
        <section className="card">
          <h3 style={{ fontSize: '1.125rem', fontWeight: 600, marginBottom: '1.5rem' }}>Ladder Teaching</h3>
          <form onSubmit={handleLadder}>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem', marginBottom: '1rem' }}>
              <div>
                <label className="label" htmlFor="ladder-session">Session ID</label>
                <input
                  id="ladder-session"
                  className="input"
                  type="text"
                  value={ladderSessionId}
                  onChange={(e) => setLadderSessionId(e.target.value)}
                  placeholder="auto-generated if empty"
                />
              </div>
              <div>
                <label className="label" htmlFor="ladder-rung">Teaching Rung</label>
                <select
                  id="ladder-rung"
                  className="input"
                  value={ladderRung}
                  onChange={(e) => setLadderRung(e.target.value as LadderStepRequest['rung'])}
                >
                  <option value="motivation">1. Motivation</option>
                  <option value="vocabulary">2. Vocabulary Map</option>
                  <option value="framework">3. Core Framework</option>
                  <option value="methods">4. Methods in Practice</option>
                  <option value="frontier">5. Frontier & Reading Path</option>
                </select>
              </div>
            </div>
            <div style={{ marginBottom: '1rem' }}>
              <label className="label" htmlFor="ladder-known">Known Frameworks (comma-separated)</label>
              <input
                id="ladder-known"
                className="input"
                type="text"
                value={ladderKnown}
                onChange={(e) => setLadderKnown(e.target.value)}
                placeholder="e.g., linear regression, maximum likelihood, Bayesian inference"
              />
            </div>
            <button type="submit" className="btn btn-primary" disabled={ladderLoading}>
              {ladderLoading ? <><span className="loading" style={{ width: '1rem', height: '1rem' }} /> Teaching...</> : 'Get Ladder Step'}
            </button>
          </form>

          {ladderResult && (
            <div style={{ marginTop: '1.5rem' }}>
              <h4 style={{ marginBottom: '0.75rem' }}>Ladder Step: {ladderRung.charAt(0).toUpperCase() + ladderRung.slice(1)}</h4>
              <div style={{ marginBottom: '1rem', lineHeight: 1.7, whiteSpace: 'pre-wrap' }}>{ladderResult.content}</div>
              {ladderResult.diagnostic_question && (
                <div style={{ padding: '1rem', background: 'rgb(37 99 235 / 0.1)', border: '1px solid var(--color-primary)', borderRadius: 'var(--radius-md)', marginBottom: '1rem' }}>
                  <strong>Diagnostic Question:</strong> {ladderResult.diagnostic_question}
                </div>
              )}
              {ladderResult.key_terms.length > 0 && (
                <div style={{ marginBottom: '1rem' }}>
                  <strong>Key Terms:</strong>
                  <ul style={{ marginTop: '0.5rem', marginLeft: '1.5rem' }}>
                    {ladderResult.key_terms.map((kt, i) => (
                      <li key={i}><strong>{kt.term}</strong>: {kt.definition} <em>(anchored to: {kt.anchored_to})</em></li>
                    ))}
                  </ul>
                </div>
              )}
              {ladderResult.verified_papers.length > 0 && (
                <div>
                  <strong>Referenced Papers:</strong>
                  <ul style={{ marginTop: '0.5rem', marginLeft: '1.5rem' }}>
                    {ladderResult.verified_papers.map((p, i) => (
                      <li key={i}>{p.title} <span className={`badge ${p.verified ? 'badge-success' : 'badge-warning'}`}>{p.verified ? 'Verified' : 'From Memory'}</span></li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          )}
        </section>
      )}

      {activeTab === 'decode' && (
        <section className="card">
          <h3 style={{ fontSize: '1.125rem', fontWeight: 600, marginBottom: '1.5rem' }}>Passage Decode Mode</h3>
          <form onSubmit={handleDecode}>
            <div style={{ marginBottom: '1rem' }}>
              <label className="label" htmlFor="decode-context">Field Context</label>
              <input
                id="decode-context"
                className="input"
                type="text"
                value={decodeContext}
                onChange={(e) => setDecodeContext(e.target.value)}
                placeholder="e.g., statistical genetics, colocalization analysis"
                required
              />
            </div>
            <div style={{ marginBottom: '1rem' }}>
              <label className="label" htmlFor="decode-passage">Passage to Decode</label>
              <textarea
                id="decode-passage"
                className="input"
                value={decodePassageText}
                onChange={(e) => setDecodePassageText(e.target.value)}
                placeholder="Paste an abstract, figure caption, referee comment, or paragraph you cannot parse..."
                rows={6}
                required
              />
            </div>
            <button type="submit" className="btn btn-primary" disabled={decodeLoading}>
              {decodeLoading ? <><span className="loading" style={{ width: '1rem', height: '1rem' }} /> Decoding...</> : 'Decode Passage'}
            </button>
          </form>

          {decodeResult && (
            <div style={{ marginTop: '1.5rem', display: 'grid', gap: '1rem' }}>
              {decodeResult.source_claims.length > 0 && (
                <div style={{ padding: '1rem', background: 'rgb(22 163 74 / 0.1)', border: '1px solid var(--color-success)', borderRadius: 'var(--radius-md)' }}>
                  <strong>Source Claims:</strong>
                  <ul style={{ marginTop: '0.5rem', marginLeft: '1.5rem' }}>
                    {decodeResult.source_claims.map((c, i) => <li key={i}>{c}</li>)}
                  </ul>
                </div>
              )}
              {decodeResult.background_needed.length > 0 && (
                <div style={{ padding: '1rem', background: 'rgb(245 158 11 / 0.1)', border: '1px solid var(--color-warning)', borderRadius: 'var(--radius-md)' }}>
                  <strong>Background Needed:</strong>
                  <ul style={{ marginTop: '0.5rem', marginLeft: '1.5rem' }}>
                    {decodeResult.background_needed.map((b, i) => <li key={i}>{b}</li>)}
                  </ul>
                </div>
              )}
              {decodeResult.inferences.length > 0 && (
                <div style={{ padding: '1rem', background: 'rgb(37 99 235 / 0.1)', border: '1px solid var(--color-primary)', borderRadius: 'var(--radius-md)' }}>
                  <strong>Inferences:</strong>
                  <ul style={{ marginTop: '0.5rem', marginLeft: '1.5rem' }}>
                    {decodeResult.inferences.map((inf, i) => <li key={i}>{inf}</li>)}
                  </ul>
                </div>
              )}
              {decodeResult.critique.length > 0 && (
                <div style={{ padding: '1rem', background: 'rgb(220 38 38 / 0.1)', border: '1px solid var(--color-error)', borderRadius: 'var(--radius-md)' }}>
                  <strong>Critique:</strong>
                  <ul style={{ marginTop: '0.5rem', marginLeft: '1.5rem' }}>
                    {decodeResult.critique.map((c, i) => <li key={i}>{c}</li>)}
                  </ul>
                </div>
              )}
            </div>
          )}
        </section>
      )}
    </div>
  )
}

export default Onboarding