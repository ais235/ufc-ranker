import React, { useState, useEffect } from 'react'
import { api } from './services/api'
import RankingsPage from './pages/RankingsPage'
import FightersPage from './pages/FightersPage'

type Page = 'home' | 'rankings' | 'fighters'

function App() {
  const [currentPage, setCurrentPage] = useState<Page>('home')
  const [backendStatus, setBackendStatus] = useState('⏳ Проверяется...')
  const [fighters, setFighters] = useState([])
  const [loading, setLoading] = useState(true)
  const [refreshing, setRefreshing] = useState(false)
  const [stats, setStats] = useState<any>(null)

  useEffect(() => {
    checkBackend()
  }, [])

  const checkBackend = async () => {
    try {
      const [fightersData, statsData] = await Promise.all([
        api.getFighters({ limit: 5 }),
        api.getStats()
      ])
      setFighters(fightersData)
      setStats(statsData)
      setBackendStatus('✅ Работает')
    } catch (error) {
      console.error('Ошибка подключения к бэкенду:', error)
      setBackendStatus('❌ Ошибка')
    } finally {
      setLoading(false)
    }
  }

  const handleRefreshUFCStats = async () => {
    setRefreshing(true)
    try {
      await api.refreshUFCStats()
      await checkBackend() // Перезагружаем данные
    } catch (error) {
      console.error('Ошибка обновления данных:', error)
    } finally {
      setRefreshing(false)
    }
  }

  const renderPage = () => {
    switch (currentPage) {
      case 'rankings':
        return <RankingsPage />
      case 'fighters':
        return <FightersPage />
      default:
        return renderHomePage()
    }
  }

  const renderHomePage = () => (
    <div className="container mx-auto px-4 py-8">
      {/* System Status */}
      <div className="bg-white rounded-lg shadow-lg p-6 mb-8">
        <h2 className="text-2xl font-bold text-gray-900 mb-4">Статус системы</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="flex items-center">
            <span className="text-lg">Бэкенд:</span>
            <span className="ml-2 text-lg">{backendStatus}</span>
          </div>
          <div className="flex items-center">
            <span className="text-lg">Фронтенд:</span>
            <span className="ml-2 text-lg text-green-600">✅ Работает</span>
          </div>
        </div>
      </div>

      {/* Refresh Button */}
      <div className="flex justify-center mb-8">
        <button
          onClick={handleRefreshUFCStats}
          disabled={refreshing}
          className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2"
        >
          {refreshing ? (
            <>
              <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
              <span>Обновление...</span>
            </>
          ) : (
            <>
              <span>🔄</span>
              <span>Обновить данные ufc.stats</span>
            </>
          )}
        </button>
      </div>

      {/* Database Statistics */}
      {stats && (
        <div className="bg-white rounded-lg shadow-lg p-6 mb-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">Статистика базы данных</h2>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="text-center">
              <div className="text-3xl font-bold text-blue-600">{stats.total_fighters}</div>
              <div className="text-gray-600">Бойцов</div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold text-green-600">{stats.total_weight_classes}</div>
              <div className="text-gray-600">Весовых категорий</div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold text-purple-600">{stats.total_events}</div>
              <div className="text-gray-600">Событий</div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold text-orange-600">{stats.total_fights}</div>
              <div className="text-gray-600">Боев</div>
            </div>
          </div>
        </div>
      )}

      {/* Test Data */}
      <div className="bg-white rounded-lg shadow-lg p-6 mb-8">
        <h2 className="text-2xl font-bold text-gray-900 mb-4">Тестовые данные</h2>
        <div className="space-y-4">
          <div>
            <h3 className="text-lg font-semibold text-gray-800 mb-2">Бойцы (первые 5):</h3>
            <div className="space-y-2">
              {fighters.map((fighter: any) => (
                <div key={fighter.id} className="flex items-center space-x-4 p-3 bg-gray-50 rounded-lg">
                  <div className="w-10 h-10 bg-blue-600 text-white rounded-full flex items-center justify-center font-bold">
                    {fighter.id}
                  </div>
                  <div>
                    <div className="font-medium">{fighter.name}</div>
                    <div className="text-sm text-gray-600">
                      {fighter.country} • {fighter.wins}-{fighter.losses}-{fighter.draws}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Welcome Message */}
      <div className="text-center bg-gradient-to-r from-blue-500 to-purple-600 text-white rounded-lg p-8">
        <h2 className="text-3xl font-bold mb-4">Добро пожаловать в UFC Ranker!</h2>
        <p className="text-xl mb-6">
          Исследуйте рейтинги, статистику бойцов и события UFC
        </p>
        <div className="space-x-4">
          <button
            onClick={() => setCurrentPage('rankings')}
            className="bg-white text-blue-600 px-6 py-3 rounded-lg font-semibold hover:bg-gray-100 transition-colors"
          >
            🥊 Рейтинги
          </button>
          <button
            onClick={() => setCurrentPage('fighters')}
            className="bg-white text-blue-600 px-6 py-3 rounded-lg font-semibold hover:bg-gray-100 transition-colors"
          >
            👊 Бойцы
          </button>
        </div>
      </div>
    </div>
  )

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-100 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Загрузка...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-100">
      {/* Header */}
      <header className="bg-white shadow-lg">
        <div className="container mx-auto px-4 py-6">
          <div className="flex items-center justify-between">
            <h1 className="text-3xl font-bold text-gray-900">
              🥊 UFC Ranker
            </h1>
            
            {/* Navigation */}
            <nav className="space-x-4">
              <button
                onClick={() => setCurrentPage('home')}
                className={`px-4 py-2 rounded-lg transition-colors ${
                  currentPage === 'home'
                    ? 'bg-blue-600 text-white'
                    : 'text-gray-600 hover:bg-gray-100'
                }`}
              >
                🏠 Главная
              </button>
              <button
                onClick={() => setCurrentPage('rankings')}
                className={`px-4 py-2 rounded-lg transition-colors ${
                  currentPage === 'rankings'
                    ? 'bg-blue-600 text-white'
                    : 'text-gray-600 hover:bg-gray-100'
                }`}
              >
                🥊 Рейтинги
              </button>
              <button
                onClick={() => setCurrentPage('fighters')}
                className={`px-4 py-2 rounded-lg transition-colors ${
                  currentPage === 'fighters'
                    ? 'bg-blue-600 text-white'
                    : 'text-gray-600 hover:bg-gray-100'
                }`}
              >
                👊 Бойцы
              </button>
            </nav>
          </div>
        </div>
      </header>

      {renderPage()}
    </div>
  )
}

export default App