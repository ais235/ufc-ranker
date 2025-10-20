import React, { useState, useEffect } from 'react'
import { useParams, Link } from 'react-router-dom'
import Layout from '../components/Layout'
import { api } from '../services/api'
import { Fighter, WeightClass, Ranking } from '../types'

const WeightClassPage: React.FC = () => {
  const { weightClass } = useParams<{ weightClass: string }>()
  const [weightClassData, setWeightClassData] = useState<WeightClass | null>(null)
  const [rankings, setRankings] = useState<Ranking[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (weightClass) {
      loadWeightClassData(weightClass)
    }
  }, [weightClass])

  const loadWeightClassData = async (weightClassName: string) => {
    try {
      setLoading(true)
      setError(null)

      // Загружаем весовые категории и рейтинги
      const [weightClassesData, rankingsData] = await Promise.all([
        api.getWeightClasses(),
        api.getRankings()
      ])

      // Находим нужную весовую категорию
      const foundWeightClass = weightClassesData.find(wc => 
        wc.name_en.toLowerCase().replace(/\s+/g, '_') === weightClassName.toLowerCase()
      )

      if (!foundWeightClass) {
        setError('Весовую категорию не найдена')
        return
      }

      setWeightClassData(foundWeightClass)
      
      // Фильтруем рейтинги для этой весовой категории
      const weightClassRankings = rankingsData
        .filter(ranking => ranking.weight_class === foundWeightClass.name_en)
        .sort((a, b) => (a.rank_position || 0) - (b.rank_position || 0))
      
      setRankings(weightClassRankings)

    } catch (error) {
      console.error('Ошибка загрузки данных весовой категории:', error)
      setError('Ошибка загрузки данных')
    } finally {
      setLoading(false)
    }
  }

  const getChampion = () => {
    return rankings.find(ranking => ranking.is_champion)
  }

  const getRegularRankings = () => {
    return rankings.filter(ranking => !ranking.is_champion)
  }

  // Функция для группировки рейтингов по строкам (по 3 в строке)
  const groupRankingsIntoRows = (rankings: Ranking[]) => {
    const rows = []
    for (let i = 0; i < rankings.length; i += 3) {
      rows.push(rankings.slice(i, i + 3))
    }
    return rows
  }

  if (loading) {
    return (
      <Layout>
        <div className="flex items-center justify-center min-h-96">
          <div className="text-center">
            <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-yellow-400 mx-auto"></div>
            <p className="mt-4 text-white text-xl">Загрузка рейтингов...</p>
          </div>
        </div>
      </Layout>
    )
  }

  if (error) {
    return (
      <Layout>
        <div className="flex items-center justify-center min-h-96">
          <div className="text-center">
            <h1 className="text-4xl font-bold text-white mb-4">Ошибка</h1>
            <p className="text-gray-300 text-xl">{error}</p>
            <Link to="/rankings" className="mt-4 btn-primary inline-block">
              Вернуться к рейтингам
            </Link>
          </div>
        </div>
      </Layout>
    )
  }

  if (!weightClassData) {
    return (
      <Layout>
        <div className="flex items-center justify-center min-h-96">
          <div className="text-center">
            <h1 className="text-4xl font-bold text-white mb-4">Весовую категорию не найдена</h1>
            <Link to="/rankings" className="mt-4 btn-primary inline-block">
              Вернуться к рейтингам
            </Link>
          </div>
        </div>
      </Layout>
    )
  }

  const champion = getChampion()
  const regularRankings = getRegularRankings()
  const rankingRows = groupRankingsIntoRows(regularRankings)

  return (
    <Layout>
      <div className="container mx-auto px-4 py-8">
        {/* Название весовой категории */}
        <div className="bg-white/10 backdrop-blur-lg border border-white/20 rounded-2xl p-8 text-center mb-8">
          <h1 className="text-5xl font-bold text-yellow-400 mb-4">
            🥊 {weightClassData.name_ru}
          </h1>
          <p className="text-white text-xl">
            {weightClassData.weight_limit && `Лимит веса: ${weightClassData.weight_limit}`}
          </p>
        </div>

        {/* Чемпион */}
        {champion && (
          <div className="bg-white/10 backdrop-blur-lg border border-white/20 rounded-2xl p-8 mb-8 relative">
            {/* Правый верхний угол с флагом */}
            <div className="absolute top-8 right-8 text-center bg-white/10 backdrop-blur-lg border border-white/20 rounded-xl p-4">
              <div className="w-10 h-8 bg-gradient-to-br from-gray-700 to-gray-800 rounded flex items-center justify-center mb-2">
                <span className="text-lg">🏳️</span>
              </div>
              <p className="text-white text-sm">{champion.fighter?.country || 'Не указана'}</p>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
              {/* Фото чемпиона */}
              <div className="lg:col-span-1">
                <div className="w-full h-80 bg-gradient-to-br from-gray-700 to-gray-800 rounded-xl flex items-center justify-center relative">
                  <div className="text-center">
                    <div className="text-8xl mb-4">👑</div>
                    <p className="text-gray-300">Фото чемпиона</p>
                  </div>
                  <div className="absolute bottom-4 left-1/2 transform -translate-x-1/2 bg-yellow-500 text-black px-4 py-2 rounded-full font-bold">
                    ЧЕМПИОН
                  </div>
                </div>
              </div>

              {/* Информация о чемпионе */}
              <div className="lg:col-span-2">
                <h2 className="text-4xl font-bold text-white mb-2">
                  {champion.fighter?.name_ru || champion.fighter?.name || 'Неизвестный боец'}
                </h2>
                
                {champion.fighter?.nickname && (
                  <p className="text-yellow-400 text-2xl mb-6">
                    "{champion.fighter.nickname}"
                  </p>
                )}

                <div className="grid grid-cols-2 gap-6 text-lg">
                  <div>
                    <span className="text-gray-400">Возраст:</span>
                    <p className="text-white font-medium">{champion.fighter?.age ? `${champion.fighter.age} лет` : 'Не указан'}</p>
                  </div>
                  <div>
                    <span className="text-gray-400">Весовая категория:</span>
                    <p className="text-white font-medium">{weightClassData.name_ru}</p>
                  </div>
                  <div>
                    <span className="text-gray-400">Рост:</span>
                    <p className="text-white font-medium">{champion.fighter?.height ? `${champion.fighter.height} см` : 'Не указан'}</p>
                  </div>
                  <div>
                    <span className="text-gray-400">Вес:</span>
                    <p className="text-white font-medium">{champion.fighter?.weight ? `${champion.fighter.weight} кг` : 'Не указан'}</p>
                  </div>
                  <div>
                    <span className="text-gray-400">Размах рук:</span>
                    <p className="text-white font-medium">{champion.fighter?.reach ? `${champion.fighter.reach} см` : 'Не указан'}</p>
                  </div>
                  <div>
                    <span className="text-gray-400">Рекорд:</span>
                    <p className="text-white font-medium">
                      {champion.fighter?.wins || 0}-{champion.fighter?.losses || 0}-{champion.fighter?.draws || 0}
                    </p>
                  </div>
                </div>

                <div className="mt-8">
                  <Link
                    to={`/fighters/${(champion.fighter?.name_en || '').replace(/\s+/g, '_')}`}
                    className="bg-yellow-500 hover:bg-yellow-600 text-black px-6 py-3 rounded-lg font-bold transition-colors"
                  >
                    Подробнее о чемпионе
                  </Link>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Рейтинги */}
        <div className="bg-white/10 backdrop-blur-lg border border-white/20 rounded-2xl p-8">
          <h2 className="text-3xl font-bold text-yellow-400 mb-8 text-center border-b-2 border-yellow-400 pb-4">
            РЕЙТИНГ ВЕСОВОЙ КАТЕГОРИИ
          </h2>
          
          <div className="space-y-6">
            {rankingRows.map((row, rowIndex) => (
              <div key={rowIndex} className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {row.map((ranking, index) => (
                  <div
                    key={ranking.id}
                    className="bg-white/5 backdrop-blur-lg border border-white/20 rounded-xl p-6 relative hover:bg-white/10 transition-all duration-300 hover:scale-105"
                  >
                    {/* Номер рейтинга */}
                    <div className="absolute -top-3 -left-3 bg-gradient-to-r from-yellow-400 to-yellow-500 text-black w-8 h-8 rounded-full flex items-center justify-center font-bold text-sm shadow-lg">
                      {ranking.rank_position || (rowIndex * 3 + index + 1)}
                    </div>

                    {/* Фото бойца */}
                    <div className="w-20 h-24 bg-gradient-to-br from-gray-700 to-gray-800 rounded-lg flex items-center justify-center mb-4 mx-auto">
                      <span className="text-2xl">👤</span>
                    </div>

                    {/* Информация о бойце */}
                    <div className="text-center">
                      <h3 className="text-xl font-bold text-yellow-400 mb-2">
                        {ranking.fighter?.name_ru || ranking.fighter?.name || 'Неизвестный боец'}
                      </h3>
                      
                      <div className="flex items-center justify-center gap-2 mb-3">
                        <span className="text-lg">🏳️</span>
                        <span className="text-gray-300 text-sm">{ranking.fighter?.country || 'Не указана'}</span>
                      </div>

                      <div className="grid grid-cols-2 gap-2 text-xs text-gray-300 mb-3">
                        <div>Возраст: {ranking.fighter?.age || 'N/A'}</div>
                        <div>Рост: {ranking.fighter?.height ? `${ranking.fighter.height} см` : 'N/A'}</div>
                        <div>Вес: {ranking.fighter?.weight ? `${ranking.fighter.weight} кг` : 'N/A'}</div>
                        <div>Размах: {ranking.fighter?.reach ? `${ranking.fighter.reach} см` : 'N/A'}</div>
                      </div>

                      <div className="text-lg font-bold text-yellow-400">
                        {ranking.fighter?.wins || 0}-{ranking.fighter?.losses || 0}-{ranking.fighter?.draws || 0}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            ))}
            
            {regularRankings.length === 0 && (
              <div className="text-center py-12">
                <div className="text-6xl mb-4">🥊</div>
                <p className="text-gray-300 text-xl">Рейтинги для этой весовой категории пока не загружены</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </Layout>
  )
}

export default WeightClassPage
