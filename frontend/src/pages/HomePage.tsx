import React, { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import Layout from '../components/Layout'
import { api } from '../services/api'

const HomePage: React.FC = () => {
  const [stats, setStats] = useState<any>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadStats()
  }, [])

  const loadStats = async () => {
    try {
      const statsData = await api.getStats()
      setStats(statsData)
    } catch (error) {
      console.error('Ошибка загрузки статистики:', error)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <Layout>
        <div className="flex items-center justify-center min-h-96">
          <div className="text-center">
            <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-yellow-400 mx-auto"></div>
            <p className="mt-4 text-white text-xl">Загрузка...</p>
          </div>
        </div>
      </Layout>
    )
  }

  return (
    <Layout>
      {/* Hero секция */}
      <div className="card text-center mb-8">
        <h1 className="text-4xl md:text-6xl font-bold mb-6 text-yellow-400">
          🥊 UFC Ranker
        </h1>
        <p className="text-xl md:text-2xl text-gray-300 mb-8 max-w-3xl mx-auto">
          Полная база данных UFC с рейтингами бойцов, статистикой боев и предстоящими событиями
        </p>
        
        <div className="flex flex-col sm:flex-row justify-center gap-4">
          <Link to="/rankings" className="btn-primary">
            🥊 Рейтинги бойцов
          </Link>
          <Link to="/events" className="btn-secondary">
            📅 События UFC
          </Link>
          <Link to="/fighters" className="btn-secondary">
            👊 База бойцов
          </Link>
        </div>
      </div>

      {/* Статистика */}
      {stats && (
        <div className="card mb-8">
          <h2 className="section-title">📊 Статистика UFC</h2>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
            <div className="text-center">
              <div className="text-3xl font-bold text-yellow-400 mb-2">
                {stats.total_fighters}
              </div>
              <div className="text-gray-300">Бойцов</div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold text-yellow-400 mb-2">
                {stats.total_events}
              </div>
              <div className="text-gray-300">Событий</div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold text-yellow-400 mb-2">
                {stats.total_fights}
              </div>
              <div className="text-gray-300">Боев</div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold text-yellow-400 mb-2">
                {stats.total_weight_classes}
              </div>
              <div className="text-gray-300">Весовых категорий</div>
            </div>
          </div>
        </div>
      )}

      {/* Быстрые ссылки */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Рейтинги */}
        <div className="card">
          <h3 className="text-2xl font-bold text-yellow-400 mb-4 text-center">
            🥊 Рейтинги
          </h3>
          <p className="text-gray-300 mb-6 text-center">
            Актуальные рейтинги бойцов по весовым категориям
          </p>
          <div className="space-y-3">
            <Link to="/rankings" className="block w-full btn-secondary text-center">
              Все рейтинги
            </Link>
            <Link to="/rankings/Lightweight" className="block w-full btn-secondary text-center">
              Легкий вес
            </Link>
            <Link to="/rankings/Welterweight" className="block w-full btn-secondary text-center">
              Полусредний вес
            </Link>
            <Link to="/rankings/Middleweight" className="block w-full btn-secondary text-center">
              Средний вес
            </Link>
          </div>
        </div>

        {/* События */}
        <div className="card">
          <h3 className="text-2xl font-bold text-yellow-400 mb-4 text-center">
            📅 События
          </h3>
          <p className="text-gray-300 mb-6 text-center">
            Предстоящие и прошедшие события UFC
          </p>
          <div className="space-y-3">
            <Link to="/events" className="block w-full btn-secondary text-center">
              Все события
            </Link>
            <Link to="/events?upcoming=true" className="block w-full btn-secondary text-center">
              Предстоящие
            </Link>
            <Link to="/events?past=true" className="block w-full btn-secondary text-center">
              Прошедшие
            </Link>
          </div>
        </div>

        {/* Бойцы */}
        <div className="card">
          <h3 className="text-2xl font-bold text-yellow-400 mb-4 text-center">
            👊 Бойцы
          </h3>
          <p className="text-gray-300 mb-6 text-center">
            Полная база данных бойцов UFC
          </p>
          <div className="space-y-3">
            <Link to="/fighters" className="block w-full btn-secondary text-center">
              Все бойцы
            </Link>
            <Link to="/fighters?search=champion" className="block w-full btn-secondary text-center">
              Чемпионы
            </Link>
            <Link to="/fighters?search=top" className="block w-full btn-secondary text-center">
              Топ бойцы
            </Link>
          </div>
        </div>
      </div>
    </Layout>
  )
}

export default HomePage