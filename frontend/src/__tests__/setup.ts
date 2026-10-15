import '@testing-library/jest-dom'
import { vi } from 'vitest'

Object.defineProperty(import.meta, 'env', {
  value: {
    VITE_API_BASE: '/api',
  },
  writable: true,
})

vi.mock('axios', () => ({
  default: {
    create: vi.fn(() => ({
      get: vi.fn(),
      post: vi.fn(),
      put: vi.fn(),
      delete: vi.fn(),
      interceptors: {
        request: { use: vi.fn() },
        response: { use: vi.fn() },
      },
    })),
  },
}))