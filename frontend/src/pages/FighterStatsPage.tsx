import React, { useState, useEffect } from 'react'
import { useParams } from 'react-router-dom'
import { FighterStatsSummary, Fight } from '../types'
import { api } from '../services/api'
import FighterStatsCard from '../components/FighterStatsCard'

const FighterStatsPage: React.FC = () => {
  const { fighterId } = useParams<{ fighterId: string }>()
  const [stats, setStats] = useState<FighterStatsSummary | null>(null)
  const [fights, setFights] = useState<Fight[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (fighterId) {
      loadFighterData(parseInt(fighterId))
    }
  }, [fighterId])

  const loadFighterData = async (id: number) => {
    try {
      setLoading(true)
      setError(null)

      const [statsData, fightsData] = await Promise.all([
        api.getFighterStats(id),
        api.getFighterFights(id, 10)
      ])

      setStats(statsData)
      setFights(fightsData)
    } catch (err) {
      setError('Ошибка при загрузке данных бойца')
      console.error('Error loading fighter data:', err)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-100 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Загрузка статистики бойца...</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-100 flex items-center justify-center">
        <div className="text-center">
          <div className="text-red-600 text-6xl mb-4">❌</div>
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Ошибка</h2>
          <p className="text-gray-600">{error}</p>
        </div>
      </div>
    )
  }

  if (!stats) {
    return (
      <div className="min-h-screen bg-gray-100 flex items-center justify-center">
        <div className="text-center">
          <div className="text-gray-400 text-6xl mb-4">🥊</div>
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Боец не найден</h2>
          <p className="text-gray-600">Статистика для данного бойца недоступна</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-100">
      {/* Заголовок */}
      <div className="bg-ufc-dark text-white py-8">
        <div className="container mx-auto px-4">
          <h1 className="text-4xl font-bold mb-2">Статистика бойца</h1>
          <p className="text-lg text-gray-300">
            Детальная статистика выступлений в UFC
          </p>
        </div>
      </div>

      {/* Основной контент */}
      <div className="container mx-auto px-4 py-8">
        {/* Статистика бойца */}
        <div className="mb-8">
          <FighterStatsCard stats={stats} />
        </div>

        {/* Последние бои */}
        {fights.length > 0 && (
          <div className="bg-white rounded-lg shadow-lg p-6">
            <h3 className="text-2xl font-bold text-gray-900 mb-6">Последние бои</h3>
            <div className="space-y-4">
              {fights.map((fight) => (
                <div key={fight.id} className="border border-gray-200 rounded-lg p-4 hover:bg-gray-50 transition-colors">
                  <div className="flex justify-between items-start">
                    <div className="flex-1">
                      <div className="flex items-center space-x-4 mb-2">
                        <span className="font-semibold text-lg">{fight.fighter1.name_ru}</span>
                        <span className="text-gray-400">vs</span>
                        <span className="font-semibold text-lg">{fight.fighter2.name_ru}</span>
                      </div>
                      <div className="text-sm text-gray-600 space-y-1">
                        <p><strong>Событие:</strong> {fight.event.name}</p>
                        <p><strong>Категория:</strong> {fight.weight_class.name_ru}</p>
                        {fight.fight_date && (
                          <p><strong>Дата:</strong> {new Date(fight.fight_date).toLocaleDateString('ru-RU')}</p>
                        )}
                        {fight.result && (
                          <p><strong>Результат:</strong> {fight.result}</p>
                        )}
                      </div>
                    </div>
                    <div className="text-right">
                      {fight.is_title_fight && (
                        <span className="inline-block bg-yellow-100 text-yellow-800 text-xs font-semibold px-2 py-1 rounded-full mb-2">
                          Титульный бой
                        </span>
                      )}
                      {fight.is_main_event && (
                        <span className="inline-block bg-red-100 text-red-800 text-xs font-semibold px-2 py-1 rounded-full">
                          Главный бой
                        </span>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default FighterStatsPage
