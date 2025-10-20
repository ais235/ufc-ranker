import React, { useState, useEffect } from 'react'
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import { api } from './services/api'
import RankingsPage from './pages/RankingsPage'
import WeightClassPage from './pages/WeightClassPage'
import FightersPage from './pages/FightersPage'
import FighterPage from './pages/FighterPage'
import EventsPage from './pages/EventsPage'
import EventPage from './pages/EventPage'
import HomePage from './pages/HomePage'

function App() {
  const [backendStatus, setBackendStatus] = useState('⏳ Проверяется...')
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    checkBackend()
  }, [])

  const checkBackend = async () => {
    try {
      await api.getStats()
      setBackendStatus('✅ Работает')
    } catch (error) {
      console.error('Ошибка подключения к бэкенду:', error)
      setBackendStatus('❌ Ошибка')
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-900 to-gray-800 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-yellow-400 mx-auto"></div>
          <p className="mt-4 text-white text-xl">Загрузка...</p>
        </div>
      </div>
    )
  }

  return (
    <Router>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/rankings" element={<RankingsPage />} />
        <Route path="/rankings/:weightClass" element={<WeightClassPage />} />
        <Route path="/fighters" element={<FightersPage />} />
        <Route path="/fighters/:fighterName" element={<FighterPage />} />
        <Route path="/events" element={<EventsPage />} />
        <Route path="/events/:eventId" element={<EventPage />} />
      </Routes>
    </Router>
  )
}

export default App