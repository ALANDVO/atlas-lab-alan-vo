import axios, { AxiosError, InternalAxiosRequestConfig } from 'axios'

declare global {
  interface ImportMetaEnv {
    readonly VITE_API_BASE: string
  }
  interface ImportMeta {
    readonly env: ImportMetaEnv
  }
}

const API_BASE = import.meta.env.VITE_API_BASE || '/api'

export const api = axios.create({
  baseURL: API_BASE,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: true,
})

api.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const token = sessionStorage.getItem('access_token')
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error: AxiosError) => Promise.reject(error)
)

api.interceptors.response.use(
  (response) => response,
  (error: AxiosError) => {
    if (error.response?.status === 401) {
      sessionStorage.removeItem('access_token')
      sessionStorage.removeItem('refresh_token')
      if (window.location.pathname !== '/login') {
        window.location.href = '/login'
      }
    }
    return Promise.reject(error)
  }
)

export interface HealthResponse {
  status: string
  app: string
  version: string
  environment: string
}

export async function getHealth(): Promise<HealthResponse> {
  const { data } = await api.get<HealthResponse>('/v1/health')
  return data
}

export async function getDbHealth(): Promise<{ status: string; database: string; error?: string }> {
  const { data } = await api.get('/v1/health/db')
  return data
}

export interface Skill {
  id: string
  name: string
  description: string
  category: string
  version: string
  author: string
}

export async function listSkills(): Promise<Skill[]> {
  const { data } = await api.get<{ skills: Skill[] }>('/v1/skills/')
  return data.skills
}

export interface LocusCompareRequest {
  gene: string
  tissue: string
  outcome_trait: string
  population: string
  sentinel_snp: string
  window_kb: number
}

export interface LocusCompareResponse {
  plot_url: string
  exposure_count: number
  outcome_count: number
  palindromic_excluded: number
  ld_computed: boolean
}

export async function runLocusCompare(request: LocusCompareRequest): Promise<LocusCompareResponse> {
  const { data } = await api.post<LocusCompareResponse>('/v1/genetics/locuscompare/workflow', request)
  return data
}

export interface OnboardingAssessRequest {
  field: string
  user_background: string[]
}

export interface OnboardingAssessResponse {
  prerequisites: string[]
  field_maturity: 'settled' | 'emerging' | 'contested'
}

export async function assessPrerequisites(request: OnboardingAssessRequest): Promise<OnboardingAssessResponse> {
  const { data } = await api.post<OnboardingAssessResponse>('/v1/onboarding/assess', request)
  return data
}

export interface LadderStepRequest {
  session_id: string
  rung: 'motivation' | 'vocabulary' | 'framework' | 'methods' | 'frontier'
  user_known_frameworks: string[]
}

export interface LadderStepResponse {
  content: string
  diagnostic_question: string
  key_terms: { term: string; definition: string; anchored_to: string }[]
  verified_papers: { title: string; verified: boolean }[]
}

export async function ladderStep(request: LadderStepRequest): Promise<LadderStepResponse> {
  const { data } = await api.post<LadderStepResponse>('/v1/onboarding/ladder/step', request)
  return data
}

export interface DecodeRequest {
  passage: string
  field_context: string
}

export interface DecodeResponse {
  source_claims: string[]
  background_needed: string[]
  inferences: string[]
  critique: string[]
}

export async function decodePassage(request: DecodeRequest): Promise<DecodeResponse> {
  const { data } = await api.post<DecodeResponse>('/v1/onboarding/decode', request)
  return data
}