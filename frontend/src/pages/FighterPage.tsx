import React, { useState, useEffect } from 'react'
import { useParams, Link } from 'react-router-dom'
import Layout from '../components/Layout'
import { api } from '../services/api'
import { Fighter, Fight, WeightClass } from '../types'

const FighterPage: React.FC = () => {
  const { fighterName } = useParams<{ fighterName: string }>()
  const [fighter, setFighter] = useState<Fighter | null>(null)
  const [fights, setFights] = useState<Fight[]>([])
  const [weightClass, setWeightClass] = useState<WeightClass | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (fighterName) {
      loadFighterData(fighterName)
    }
  }, [fighterName])

  const loadFighterData = async (fighterIdentifier: string) => {
    try {
      setLoading(true)
      setError(null)

      // Загружаем всех бойцов и ищем нужного
      const fighters = await api.getFighters({ limit: 1000 })
      const foundFighter = fighters.find(f => 
        f.name.toLowerCase().replace(/\s+/g, '_') === fighterIdentifier.toLowerCase()
      )

      if (!foundFighter) {
        setError('Боец не найден')
        return
      }

      setFighter(foundFighter)

      // Загружаем бои бойца
      const fighterFights = await api.getFights({ fighter_id: foundFighter.id })
      setFights(fighterFights)

      // Загружаем весовую категорию
      if (foundFighter.weight_class_id) {
        const weightClasses = await api.getWeightClasses()
        const foundWeightClass = weightClasses.find(wc => wc.id === foundFighter.weight_class_id)
        setWeightClass(foundWeightClass || null)
      }

    } catch (error) {
      console.error('Ошибка загрузки бойца:', error)
      setError('Ошибка загрузки данных бойца')
    } finally {
      setLoading(false)
    }
  }

  const getRecentFights = () => {
    return fights.slice(0, 5) // Последние 5 боев
  }

  const getFightResult = (fight: Fight) => {
    // Определяем результат для нашего бойца
    if (fight.fighter1_name === fighter?.name) {
      if (fight.is_win === '1') return { result: 'Победа', color: 'text-green-400' }
      if (fight.is_loss === '1') return { result: 'Поражение', color: 'text-red-400' }
      if (fight.is_draw === '1') return { result: 'Ничья', color: 'text-yellow-400' }
      if (fight.is_nc === '1') return { result: 'Не состоялся', color: 'text-gray-400' }
    } else if (fight.fighter2_name === fighter?.name) {
      if (fight.is_win === '1') return { result: 'Поражение', color: 'text-red-400' }
      if (fight.is_loss === '1') return { result: 'Победа', color: 'text-green-400' }
      if (fight.is_draw === '1') return { result: 'Ничья', color: 'text-yellow-400' }
      if (fight.is_nc === '1') return { result: 'Не состоялся', color: 'text-gray-400' }
    }
    return { result: 'Неизвестно', color: 'text-gray-400' }
  }

  if (loading) {
    return (
      <Layout>
        <div className="flex items-center justify-center min-h-96">
          <div className="text-center">
            <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-yellow-400 mx-auto"></div>
            <p className="mt-4 text-white text-xl">Загрузка бойца...</p>
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
            <Link to="/fighters" className="mt-4 btn-primary inline-block">
              Вернуться к бойцам
            </Link>
          </div>
        </div>
      </Layout>
    )
  }

  if (!fighter) {
    return (
      <Layout>
        <div className="flex items-center justify-center min-h-96">
          <div className="text-center">
            <h1 className="text-4xl font-bold text-white mb-4">Боец не найден</h1>
            <Link to="/fighters" className="mt-4 btn-primary inline-block">
              Вернуться к бойцам
            </Link>
          </div>
        </div>
      </Layout>
    )
  }

  return (
    <Layout>
      {/* Основная карточка бойца */}
      <div className="card mb-8 relative">
        {/* Флаг страны */}
        <div className="absolute top-6 right-6">
          <div className="bg-gray-800 bg-opacity-50 p-4 rounded-lg border border-gray-700">
            <div className="w-10 h-8 bg-gradient-to-br from-gray-700 to-gray-800 rounded flex items-center justify-center mb-2">
              <span className="text-lg">🏳️</span>
            </div>
            <p className="text-gray-300 text-sm">{fighter.country || 'Не указана'}</p>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {/* Фото бойца */}
          <div className="md:col-span-1">
            <div className="w-full h-80 bg-gradient-to-br from-gray-700 to-gray-800 rounded-lg flex items-center justify-center">
              <div className="text-center">
                <div className="text-6xl mb-4">👊</div>
                <p className="text-gray-300">Фото бойца</p>
              </div>
            </div>
          </div>

          {/* Информация о бойце */}
          <div className="md:col-span-2">
            <h1 className="text-4xl font-bold text-white mb-2">
              {fighter.name_ru || fighter.name}
            </h1>
            
            {fighter.nickname && (
              <p className="text-yellow-400 text-xl mb-6">
                "{fighter.nickname}"
              </p>
            )}

            <div className="grid grid-cols-2 gap-6 mb-6">
              <div>
                <span className="text-gray-400">Страна:</span>
                <p className="text-white font-medium">{fighter.country || 'Не указана'}</p>
              </div>
              <div>
                <span className="text-gray-400">Возраст:</span>
                <p className="text-white font-medium">{fighter.age ? `${fighter.age} лет` : 'Не указан'}</p>
              </div>
              <div>
                <span className="text-gray-400">Рост:</span>
                <p className="text-white font-medium">{fighter.height ? `${fighter.height} см` : 'Не указан'}</p>
              </div>
              <div>
                <span className="text-gray-400">Размах рук:</span>
                <p className="text-white font-medium">{fighter.reach ? `${fighter.reach} см` : 'Не указан'}</p>
              </div>
              <div>
                <span className="text-gray-400">Вес:</span>
                <p className="text-white font-medium">{fighter.weight ? `${fighter.weight} кг` : 'Не указан'}</p>
              </div>
              <div>
                <span className="text-gray-400">Категория:</span>
                <p className="text-white font-medium">
                  {weightClass ? (weightClass.name_ru || weightClass.name) : 'Не указана'}
                </p>
              </div>
            </div>

            {/* Рекорд */}
            <div className="bg-gray-800 bg-opacity-50 p-6 rounded-lg mb-6">
              <h3 className="text-xl font-bold text-yellow-400 mb-4">Боевой рекорд</h3>
              <div className="grid grid-cols-4 gap-4 text-center">
                <div>
                  <div className="text-3xl font-bold text-green-400">{fighter.wins}</div>
                  <div className="text-gray-400">Побед</div>
                </div>
                <div>
                  <div className="text-3xl font-bold text-red-400">{fighter.losses}</div>
                  <div className="text-gray-400">Поражений</div>
                </div>
                <div>
                  <div className="text-3xl font-bold text-yellow-400">{fighter.draws}</div>
                  <div className="text-gray-400">Ничьих</div>
                </div>
                <div>
                  <div className="text-3xl font-bold text-white">{fighter.wins + fighter.losses + fighter.draws}</div>
                  <div className="text-gray-400">Всего боев</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Последние бои */}
      {fights.length > 0 && (
        <div className="card">
          <h2 className="text-2xl font-bold text-yellow-400 mb-6 border-b-2 border-yellow-400 pb-3">
            Последние бои
          </h2>
          
          <div className="space-y-4">
            {getRecentFights().map((fight) => {
              const fightResult = getFightResult(fight)
              const opponent = fight.fighter1_name === fighter.name ? fight.fighter2_name : fight.fighter1_name
              
              return (
                <div key={fight.id} className="bg-gray-800 bg-opacity-50 rounded-lg p-6 border border-gray-700">
                  <div className="flex justify-between items-center">
                    <div>
                      <h3 className="text-xl font-bold text-white mb-2">
                        vs {opponent}
                      </h3>
                      <p className="text-gray-300">{fight.weight_class}</p>
                      <p className="text-gray-400 text-sm">
                        {fight.fight_date ? new Date(fight.fight_date).toLocaleDateString('ru-RU') : 'Дата неизвестна'}
                      </p>
                    </div>
                    
                    <div className="text-right">
                      <div className={`text-2xl font-bold ${fightResult.color}`}>
                        {fightResult.result}
                      </div>
                      {fight.method && (
                        <p className="text-gray-300 text-sm">{fight.method}</p>
                      )}
                      {fight.round && (
                        <p className="text-gray-400 text-xs">Раунд {fight.round}</p>
                      )}
                    </div>
                  </div>
                </div>
              )
            })}
          </div>

          {fights.length > 5 && (
            <div className="text-center mt-6">
              <p className="text-gray-400">
                Показаны последние 5 боев из {fights.length} общих
              </p>
            </div>
          )}
        </div>
      )}

      {fights.length === 0 && (
        <div className="card text-center">
          <div className="text-6xl mb-4">🥊</div>
          <p className="text-gray-300 text-xl">Информация о боях не найдена</p>
        </div>
      )}
    </Layout>
  )
}

export default FighterPage