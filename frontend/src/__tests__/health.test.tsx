import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import { BrowserRouter } from 'react-router-dom'
import Dashboard from '../pages/Dashboard'
import { getHealth, getDbHealth } from '../api/client'

vi.mock('../api/client', () => ({
  api: {
    get: vi.fn(),
    interceptors: { request: { use: vi.fn() }, response: { use: vi.fn() } },
  },
  getHealth: vi.fn(),
  getDbHealth: vi.fn(),
}))

const renderWithRouter = (component: React.ReactNode) => {
  return render(<BrowserRouter>{component}</BrowserRouter>)
}

describe('Dashboard', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders loading state initially', () => {
    const { getByRole } = renderWithRouter(<Dashboard />)
    expect(getByRole('status')).toBeInTheDocument()
  })

  it('displays health status when loaded', async () => {
    vi.mocked(getHealth).mockResolvedValue({
      status: 'ok',
      app: 'atlas-lab',
      version: '1.0.0',
      environment: 'development',
    })
    vi.mocked(getDbHealth).mockResolvedValue({
      status: 'ok',
      database: 'connected',
    })

    renderWithRouter(<Dashboard />)

    await waitFor(() => {
      expect(screen.getByText('Healthy')).toBeInTheDocument()
    })
    expect(screen.getByText('Connected')).toBeInTheDocument()
    expect(screen.getByText('development')).toBeInTheDocument()
  })

  it('shows workflow cards', async () => {
    vi.mocked(getHealth).mockResolvedValue({
      status: 'ok',
      app: 'atlas-lab',
      version: '1.0.0',
      environment: 'development',
    })
    vi.mocked(getDbHealth).mockResolvedValue({
      status: 'ok',
      database: 'connected',
    })

    renderWithRouter(<Dashboard />)

    await waitFor(() => {
      expect(screen.getByText('Statistical Genetics: Locus Compare')).toBeInTheDocument()
      expect(screen.getByText('Field Onboarding')).toBeInTheDocument()
      expect(screen.getByText('Skill Registry')).toBeInTheDocument()
    })
  })
})