import { Routes, Route, Navigate } from 'react-router-dom'
import { useEffect, useState } from 'react'
import Layout from './components/Layout'
import Dashboard from './pages/Dashboard'
import Skills from './pages/Skills'
import Genetics from './pages/Genetics'
import Onboarding from './pages/Onboarding'
import Login from './pages/Login'
import { api } from './api/client'

function App() {
  const [initialized, setInitialized] = useState(false)

  useEffect(() => {
    api.get('/api/v1/health')
      .then(() => setInitialized(true))
      .catch(() => setInitialized(true))
  }, [])

  if (!initialized) {
    return (
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: '100vh' }}>
        <div className="loading" />
      </div>
    )
  }

  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route element={<Layout />}>
        <Route path="/" element={<Dashboard />} />
        <Route path="/skills" element={<Skills />} />
        <Route path="/genetics" element={<Genetics />} />
        <Route path="/onboarding" element={<Onboarding />} />
      </Route>
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}

export default App