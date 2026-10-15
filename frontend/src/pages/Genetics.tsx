import { useState } from 'react'
import { LocusCompareRequest, LocusCompareResponse, runLocusCompare } from '../api/client'

function Genetics() {
  const [form, setForm] = useState<LocusCompareRequest>({
    gene: 'SORT1',
    tissue: 'liver',
    outcome_trait: 'triglycerides',
    population: 'EUR',
    sentinel_snp: 'rs12740374',
    window_kb: 500,
  })
  const [result, setResult] = useState<LocusCompareResponse | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError(null)
    try {
      const res = await runLocusCompare(form)
      setResult(res)
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : 'Unknown error')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div>
      <header style={{ marginBottom: '2rem' }}>
        <h2 style={{ fontSize: '1.75rem', fontWeight: 600, marginBottom: '0.5rem' }}>Statistical Genetics: Locus Compare</h2>
        <p style={{ color: 'var(--color-text-muted)' }}>
          Generate canonical 4-panel locus compare plots for colocalization analysis.
          Fetches GWAS Catalog outcome data, eQTL Catalogue exposure data, computes LD from 1000 Genomes,
          and renders harmonized plots with palindromic variant exclusion.
        </p>
      </header>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '2rem', alignItems: 'start' }}>
        <section className="card">
          <h3 style={{ fontSize: '1.125rem', fontWeight: 600, marginBottom: '1.5rem' }}>Workflow Parameters</h3>
          <form onSubmit={handleSubmit}>
            <div style={{ marginBottom: '1rem' }}>
              <label className="label" htmlFor="gene">Gene Symbol</label>
              <input
                id="gene"
                className="input"
                type="text"
                value={form.gene}
                onChange={(e) => setForm({ ...form, gene: e.target.value })}
                placeholder="e.g., SORT1"
                required
              />
            </div>
            <div style={{ marginBottom: '1rem' }}>
              <label className="label" htmlFor="tissue">Tissue (eQTL)</label>
              <input
                id="tissue"
                className="input"
                type="text"
                value={form.tissue}
                onChange={(e) => setForm({ ...form, tissue: e.target.value })}
                placeholder="e.g., liver"
                required
              />
            </div>
            <div style={{ marginBottom: '1rem' }}>
              <label className="label" htmlFor="outcome_trait">Outcome Trait (GWAS)</label>
              <input
                id="outcome_trait"
                className="input"
                type="text"
                value={form.outcome_trait}
                onChange={(e) => setForm({ ...form, outcome_trait: e.target.value })}
                placeholder="e.g., triglycerides"
                required
              />
            </div>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem', marginBottom: '1rem' }}>
              <div>
                <label className="label" htmlFor="population">Population</label>
                <select
                  id="population"
                  className="input"
                  value={form.population}
                  onChange={(e) => setForm({ ...form, population: e.target.value })}
                >
                  <option value="EUR">EUR (European)</option>
                  <option value="AFR">AFR (African)</option>
                  <option value="EAS">EAS (East Asian)</option>
                  <option value="SAS">SAS (South Asian)</option>
                  <option value="AMR">AMR (Admixed American)</option>
                </select>
              </div>
              <div>
                <label className="label" htmlFor="sentinel_snp">Sentinel SNP</label>
                <input
                  id="sentinel_snp"
                  className="input"
                  type="text"
                  value={form.sentinel_snp}
                  onChange={(e) => setForm({ ...form, sentinel_snp: e.target.value })}
                  placeholder="e.g., rs12740374"
                  required
                />
              </div>
            </div>
            <div style={{ marginBottom: '1rem' }}>
              <label className="label" htmlFor="window_kb">Window (kb)</label>
              <input
                id="window_kb"
                className="input"
                type="number"
                value={form.window_kb}
                onChange={(e) => setForm({ ...form, window_kb: Number(e.target.value) })}
                min={100}
                max={2000}
                step={100}
                required
              />
            </div>
            <button type="submit" className="btn btn-primary" disabled={loading} style={{ width: '100%' }}>
              {loading ? <><span className="loading" style={{ width: '1rem', height: '1rem' }} /> Running...</> : 'Run Locus Compare'}
            </button>
          </form>
        </section>

        <section className="card">
          <h3 style={{ fontSize: '1.125rem', fontWeight: 600, marginBottom: '1rem' }}>Results</h3>
          {error && (
            <div style={{ padding: '1rem', background: 'rgb(220 38 38 / 0.1)', border: '1px solid var(--color-error)', borderRadius: 'var(--radius-md)', color: 'var(--color-error)', marginBottom: '1rem' }}>
              {error}
            </div>
          )}
          {result && (
            <div>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '1rem', marginBottom: '1rem' }}>
                <div style={{ textAlign: 'center', padding: '1rem', background: 'var(--color-bg)', borderRadius: 'var(--radius-md)' }}>
                  <div style={{ fontSize: '1.5rem', fontWeight: 600, color: 'var(--color-primary)' }}>{result.exposure_count}</div>
                  <div style={{ fontSize: '0.75rem', color: 'var(--color-text-muted)' }}>Exposure Variants</div>
                </div>
                <div style={{ textAlign: 'center', padding: '1rem', background: 'var(--color-bg)', borderRadius: 'var(--radius-md)' }}>
                  <div style={{ fontSize: '1.5rem', fontWeight: 600, color: 'var(--color-primary)' }}>{result.outcome_count}</div>
                  <div style={{ fontSize: '0.75rem', color: 'var(--color-text-muted)' }}>Outcome Variants</div>
                </div>
                <div style={{ textAlign: 'center', padding: '1rem', background: 'var(--color-bg)', borderRadius: 'var(--radius-md)' }}>
                  <div style={{ fontSize: '1.5rem', fontWeight: 600, color: 'var(--color-warning)' }}>{result.palindromic_excluded}</div>
                  <div style={{ fontSize: '0.75rem', color: 'var(--color-text-muted)' }}>Palindromic Excluded</div>
                </div>
                <div style={{ textAlign: 'center', padding: '1rem', background: 'var(--color-bg)', borderRadius: 'var(--radius-md)' }}>
                  <span className={`badge ${result.ld_computed ? 'badge-success' : 'badge-warning'}`}>
                    {result.ld_computed ? 'LD Computed' : 'LD Failed'}
                  </span>
                </div>
              </div>
              {result.plot_url && (
                <div style={{ textAlign: 'center' }}>
                  <img src={result.plot_url} alt="Locus compare plot" style={{ maxWidth: '100%', borderRadius: 'var(--radius-md)', border: '1px solid var(--color-border)' }} />
                </div>
              )}
            </div>
          )}
          {!result && !error && !loading && (
            <div className="empty-state">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
                <rect x="3" y="3" width="18" height="18" rx="2" />
                <path d="M9 17V9" />
                <path d="M15 17V13" />
              </svg>
              <h3>No results yet</h3>
              <p>Configure parameters and run the workflow to generate a locus compare plot.</p>
            </div>
          )}
        </section>
      </div>

      <section style={{ marginTop: '2rem' }} className="card">
        <h3 style={{ fontSize: '1.125rem', fontWeight: 600, marginBottom: '1rem' }}>About This Workflow</h3>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '1rem', fontSize: '0.875rem' }}>
          <div>
            <strong>1. GWAS Catalog Fetch</strong>
            <p style={{ color: 'var(--color-text-muted)', marginTop: '0.25rem' }}>Retrieves summary statistics for the outcome trait in the specified genomic region.</p>
          </div>
          <div>
            <strong>2. eQTL Catalogue Fetch</strong>
            <p style={{ color: 'var(--color-text-muted)', marginTop: '0.25rem' }}>Retrieves expression QTL data for the gene in the specified tissue.</p>
          </div>
          <div>
            <strong>3. LD Computation (1000 Genomes)</strong>
            <p style={{ color: 'var(--color-text-muted)', marginTop: '0.25rem' }}>Computes linkage disequilibrium between the sentinel SNP and regional variants using the appropriate population panel.</p>
          </div>
          <div>
            <strong>4. Locus Compare Render</strong>
            <p style={{ color: 'var(--color-text-muted)', marginTop: '0.25rem' }}>Harmonizes exposure × outcome on variant_id, flips beta for swapped alleles, excludes palindromic A/T·G/C variants, renders 4-panel PNG.</p>
          </div>
        </div>
      </section>
    </div>
  )
}

export default Genetics