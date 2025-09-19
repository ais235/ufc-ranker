import React, { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { api } from '../services/api'
import { FighterDetail, Fight, FightStats, FighterStatsSummary } from '../types'

const FighterPage: React.FC = () => {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const [fighter, setFighter] = useState<FighterDetail | null>(null)
  const [fights, setFights] = useState<Fight[]>([])
  const [stats, setStats] = useState<FighterStatsSummary | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (id) {
      loadFighterData(parseInt(id))
    }
  }, [id])

  const loadFighterData = async (fighterId: number) => {
    try {
      setLoading(true)
      setError(null)
      
      const [fighterData, fightsData, statsData] = await Promise.all([
        api.getFighter(fighterId),
        api.getFighterFights(fighterId, 10),
        api.getFighterStats(fighterId)
      ])
      
      setFighter(fighterData)
      setFights(fightsData)
      setStats(statsData)
    } catch (err) {
      console.error('Ошибка загрузки данных бойца:', err)
      setError('Не удалось загрузить данные бойца')
    } finally {
      setLoading(false)
    }
  }

  const formatDate = (dateString?: string) => {
    if (!dateString) return 'Не указана'
    return new Date(dateString).toLocaleDateString('ru-RU')
  }

  const getResultColor = (result?: string) => {
    if (!result) return 'text-gray-500'
    if (result.toLowerCase().includes('ko') || result.toLowerCase().includes('tko')) {
      return 'text-red-600 font-bold'
    }
    if (result.toLowerCase().includes('submission')) {
      return 'text-purple-600 font-bold'
    }
    if (result.toLowerCase().includes('decision')) {
      return 'text-blue-600 font-bold'
    }
    return 'text-gray-600'
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-100 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Загрузка данных бойца...</p>
        </div>
      </div>
    )
  }

  if (error || !fighter) {
    return (
      <div className="min-h-screen bg-gray-100 flex items-center justify-center">
        <div className="text-center">
          <div className="text-6xl mb-4">😞</div>
          <h2 className="text-2xl font-bold text-gray-900 mb-4">
            {error || 'Боец не найден'}
          </h2>
          <button
            onClick={() => navigate('/fighters')}
            className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition-colors"
          >
            Вернуться к списку бойцов
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-100">
      <div className="container mx-auto px-4 py-8">
        {/* Кнопка назад */}
        <button
          onClick={() => navigate('/fighters')}
          className="mb-6 flex items-center text-blue-600 hover:text-blue-800 transition-colors"
        >
          <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
          </svg>
          Назад к списку бойцов
        </button>

        {/* Основная информация о бойце */}
        <div className="bg-white rounded-lg shadow-lg overflow-hidden mb-8">
          <div className="md:flex">
            {/* Фото бойца */}
            <div className="md:w-1/3">
              <div className="h-96 md:h-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center">
                {fighter.image_url ? (
                  <img
                    src={fighter.image_url}
                    alt={fighter.name_ru}
                    className="w-full h-full object-cover"
                  />
                ) : (
                  <div className="text-white text-8xl">🥊</div>
                )}
              </div>
            </div>

            {/* Информация */}
            <div className="md:w-2/3 p-8">
              <div className="flex items-start justify-between mb-6">
                <div>
                  <h1 className="text-4xl font-bold text-gray-900 mb-2">
                    {fighter.name_ru}
                  </h1>
                  {fighter.name_en && fighter.name_en !== fighter.name_ru && (
                    <p className="text-xl text-gray-600 mb-2">{fighter.name_en}</p>
                  )}
                  {fighter.nickname && (
                    <p className="text-lg text-blue-600 font-semibold">"{fighter.nickname}"</p>
                  )}
                </div>
                
                {fighter.country_flag_url && (
                  <img
                    src={fighter.country_flag_url}
                    alt={fighter.country}
                    className="w-12 h-8 object-cover rounded"
                  />
                )}
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
                <div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-3">Основная информация</h3>
                  <div className="space-y-2">
                    <div className="flex justify-between">
                      <span className="text-gray-600">Страна:</span>
                      <span className="font-medium">{fighter.country || 'Не указана'}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Возраст:</span>
                      <span className="font-medium">{fighter.age ? `${fighter.age} лет` : 'Не указан'}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Рост:</span>
                      <span className="font-medium">{fighter.height ? `${fighter.height} см` : 'Не указан'}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Вес:</span>
                      <span className="font-medium">{fighter.weight ? `${fighter.weight} кг` : 'Не указан'}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Размах рук:</span>
                      <span className="font-medium">{fighter.reach ? `${fighter.reach} см` : 'Не указан'}</span>
                    </div>
                  </div>
                </div>

                <div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-3">Боевой рекорд</h3>
                  <div className="space-y-2">
                    <div className="flex justify-between">
                      <span className="text-gray-600">Победы:</span>
                      <span className="font-bold text-green-600">{fighter.wins}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Поражения:</span>
                      <span className="font-bold text-red-600">{fighter.losses}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Ничьи:</span>
                      <span className="font-bold text-yellow-600">{fighter.draws}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Всего боев:</span>
                      <span className="font-bold text-blue-600">{fighter.wins + fighter.losses + fighter.draws}</span>
                    </div>
                    {fighter.fight_record && (
                      <div className="flex justify-between">
                        <span className="text-gray-600">% побед:</span>
                        <span className="font-bold text-blue-600">{fighter.fight_record.win_percentage}%</span>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Статистика боев */}
        {stats && (
          <div className="bg-white rounded-lg shadow-lg p-6 mb-8">
            <h2 className="text-2xl font-bold text-gray-900 mb-6">📊 Статистика боев</h2>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
              <div className="text-center">
                <div className="text-3xl font-bold text-blue-600">{stats.total_fights}</div>
                <div className="text-gray-600">Всего боев</div>
              </div>
              <div className="text-center">
                <div className="text-3xl font-bold text-green-600">{stats.average_significant_strikes_rate.toFixed(1)}%</div>
                <div className="text-gray-600">Точность ударов</div>
              </div>
              <div className="text-center">
                <div className="text-3xl font-bold text-purple-600">{stats.average_takedown_rate.toFixed(1)}%</div>
                <div className="text-gray-600">Тейкдауны</div>
              </div>
              <div className="text-center">
                <div className="text-3xl font-bold text-red-600">{stats.total_knockdowns}</div>
                <div className="text-gray-600">Нокдауны</div>
              </div>
            </div>
          </div>
        )}

        {/* История боев */}
        <div className="bg-white rounded-lg shadow-lg p-6">
          <h2 className="text-2xl font-bold text-gray-900 mb-6">🥊 История боев</h2>
          {fights.length > 0 ? (
            <div className="space-y-4">
              {fights.map((fight) => (
                <div key={fight.id} className="border border-gray-200 rounded-lg p-4 hover:bg-gray-50 transition-colors">
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center space-x-4">
                      <div className="text-sm text-gray-500">
                        {formatDate(fight.fight_date)}
                      </div>
                      {fight.is_title_fight && (
                        <span className="bg-yellow-100 text-yellow-800 text-xs px-2 py-1 rounded-full">
                          🏆 Титульный бой
                        </span>
                      )}
                      {fight.is_main_event && (
                        <span className="bg-blue-100 text-blue-800 text-xs px-2 py-1 rounded-full">
                          ⭐ Главный бой
                        </span>
                      )}
                    </div>
                    <div className={`text-sm font-semibold ${getResultColor(fight.result)}`}>
                      {fight.result || 'Результат неизвестен'}
                    </div>
                  </div>
                  
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-4">
                      <div className="text-lg font-semibold">
                        {fight.fighter1.name_ru}
                      </div>
                      <div className="text-gray-400">vs</div>
                      <div className="text-lg font-semibold">
                        {fight.fighter2.name_ru}
                      </div>
                    </div>
                    <div className="text-sm text-gray-500">
                      {fight.event.name}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-8">
              <div className="text-4xl mb-4">🥊</div>
              <p className="text-gray-500">История боев не найдена</p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default FighterPage