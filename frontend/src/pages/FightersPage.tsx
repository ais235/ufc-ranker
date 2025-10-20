import React, { useState, useEffect } from 'react'
import { useParams, Link } from 'react-router-dom'
import Layout from '../components/Layout'
import { api } from '../services/api'
import { Fighter, WeightClass } from '../types'

const FightersPage: React.FC = () => {
  const { fighterName } = useParams<{ fighterName?: string }>()
  const [fighters, setFighters] = useState<Fighter[]>([])
  const [weightClasses, setWeightClasses] = useState<WeightClass[]>([])
  const [selectedWeightClass, setSelectedWeightClass] = useState<number | null>(null)
  const [searchTerm, setSearchTerm] = useState('')
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadData()
  }, [])

  const loadData = async () => {
    try {
      const [fightersData, weightClassesData] = await Promise.all([
        api.getFighters({ limit: 20 }), // Ограничиваем 20 бойцами
        api.getWeightClasses()
      ])
      setFighters(fightersData)
      setWeightClasses(weightClassesData)
    } catch (error) {
      console.error('Ошибка загрузки данных:', error)
    } finally {
      setLoading(false)
    }
  }

  const filteredFighters = fighters.filter(fighter => {
    const matchesSearch = fighter.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         fighter.name_ru.toLowerCase().includes(searchTerm.toLowerCase())
    const matchesWeightClass = selectedWeightClass === null || fighter.weight_class_id === selectedWeightClass
    return matchesSearch && matchesWeightClass
  })

  const getWeightClassName = (weightClassId: number | undefined) => {
    if (!weightClassId) return 'Неизвестная категория'
    const weightClass = weightClasses.find(wc => wc.id === weightClassId)
    return weightClass ? (weightClass.name_ru || weightClass.name) : 'Неизвестная категория'
  }

  const getFighterUrl = (fighter: Fighter) => {
    const name = fighter.name.replace(/\s+/g, '_')
    return `/fighters/${name}`
  }

  if (loading) {
    return (
      <Layout>
        <div className="flex items-center justify-center min-h-96">
          <div className="text-center">
            <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-yellow-400 mx-auto"></div>
            <p className="mt-4 text-white text-xl">Загрузка бойцов...</p>
          </div>
        </div>
      </Layout>
    )
  }

  return (
    <Layout>
      {/* Заголовок */}
      <div className="card text-center mb-8">
        <h1 className="section-title">👊 База бойцов UFC</h1>
        <p className="text-gray-300 text-lg">
          Полная база данных бойцов UFC с детальной информацией
        </p>
      </div>

      {/* Фильтры */}
      <div className="card mb-8">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Поиск */}
          <div>
            <label className="block text-yellow-400 font-semibold mb-2">
              Поиск бойца
            </label>
            <input
              type="text"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              placeholder="Введите имя бойца..."
              className="w-full px-4 py-3 bg-gray-800 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:border-yellow-400 focus:outline-none"
            />
          </div>

          {/* Весовая категория */}
          <div>
            <label className="block text-yellow-400 font-semibold mb-2">
              Весовая категория
            </label>
            <select
              value={selectedWeightClass || ''}
              onChange={(e) => setSelectedWeightClass(e.target.value ? parseInt(e.target.value) : null)}
              className="w-full px-4 py-3 bg-gray-800 border border-gray-600 rounded-lg text-white focus:border-yellow-400 focus:outline-none"
            >
              <option value="">Все категории</option>
              {weightClasses.map(weightClass => (
                <option key={weightClass.id} value={weightClass.id}>
                  {weightClass.name_ru || weightClass.name}
                </option>
              ))}
            </select>
          </div>
        </div>
      </div>

      {/* Список бойцов */}
      <div className="card">
        <h2 className="text-2xl font-bold text-yellow-400 mb-6 text-center">
          Бойцы UFC ({filteredFighters.length})
        </h2>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredFighters.map((fighter) => (
            <div
              key={fighter.id}
              className="bg-gray-800 bg-opacity-50 rounded-lg p-6 border border-gray-700 hover:bg-opacity-70 transition-all"
            >
              {/* Фото бойца */}
              <div className="w-full h-48 bg-gradient-to-br from-gray-700 to-gray-800 rounded-lg mb-4 flex items-center justify-center">
                <div className="text-center">
                  <div className="text-6xl mb-2">👊</div>
                  <p className="text-gray-300 text-sm">Фото бойца</p>
                </div>
              </div>

              {/* Информация о бойце */}
              <div className="text-center">
                <h3 className="text-xl font-bold text-white mb-2">
                  {fighter.name_ru || fighter.name}
                </h3>
                
                {fighter.nickname && (
                  <p className="text-yellow-400 font-medium mb-2">
                    "{fighter.nickname}"
                  </p>
                )}

                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-gray-400">Страна:</span>
                    <span className="text-white">{fighter.country || 'Не указана'}</span>
                  </div>
                  
                  <div className="flex justify-between">
                    <span className="text-gray-400">Категория:</span>
                    <span className="text-white">{getWeightClassName(fighter.weight_class_id)}</span>
                  </div>
                  
                  <div className="flex justify-between">
                    <span className="text-gray-400">Рост:</span>
                    <span className="text-white">{fighter.height ? `${fighter.height} см` : 'Не указан'}</span>
                  </div>
                  
                  <div className="flex justify-between">
                    <span className="text-gray-400">Размах рук:</span>
                    <span className="text-white">{fighter.reach ? `${fighter.reach} см` : 'Не указан'}</span>
                  </div>
                  
                  <div className="flex justify-between">
                    <span className="text-gray-400">Рекорд:</span>
                    <span className="text-white font-bold">
                      {fighter.wins}-{fighter.losses}-{fighter.draws}
                    </span>
                  </div>
                </div>

                <Link
                  to={getFighterUrl(fighter)}
                  className="mt-4 inline-block w-full btn-primary text-center"
                >
                  Подробнее
                </Link>
              </div>
            </div>
          ))}
        </div>

        {filteredFighters.length === 0 && (
          <div className="text-center py-12">
            <div className="text-6xl mb-4">👊</div>
            <p className="text-gray-300 text-xl">Бойцы не найдены</p>
          </div>
        )}
      </div>
    </Layout>
  )
}

export default FightersPage