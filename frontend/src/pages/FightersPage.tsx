import React, { useState, useEffect } from 'react'
import { api } from '../services/api'
import { Fighter, WeightClass } from '../types'

const FightersPage: React.FC = () => {
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
        api.getFighters({ limit: 100 }),
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
    const searchName = (fighter.name_ru || fighter.name || '').toLowerCase()
    const searchCountry = (fighter.country || '').toLowerCase()
    const searchTermLower = searchTerm.toLowerCase()
    
    const matchesSearch = searchName.includes(searchTermLower) || searchCountry.includes(searchTermLower)
    const matchesWeightClass = selectedWeightClass === null || fighter.weight_class_id === selectedWeightClass
    return matchesSearch && matchesWeightClass
  })

  const getWeightClassName = (weightClassId: number) => {
    const weightClass = weightClasses.find(wc => wc.id === weightClassId)
    return weightClass?.name || 'Неизвестная категория'
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-100 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Загрузка бойцов...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-100">
      <div className="container mx-auto px-4 py-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-8 text-center">
          👊 Бойцы UFC
        </h1>

        {/* Фильтры */}
        <div className="mb-8 bg-white rounded-lg shadow-lg p-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* Поиск */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Поиск по имени или стране:
              </label>
              <input
                type="text"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                placeholder="Введите имя бойца или страну..."
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>

            {/* Весовая категория */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Весовая категория:
              </label>
              <select
                value={selectedWeightClass || ''}
                onChange={(e) => setSelectedWeightClass(e.target.value ? Number(e.target.value) : null)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="">Все категории</option>
                {weightClasses.map(weightClass => (
                  <option key={weightClass.id} value={weightClass.id}>
                    {weightClass.name}
                  </option>
                ))}
              </select>
            </div>
          </div>
        </div>

        {/* Список бойцов */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
          {filteredFighters.map((fighter) => (
            <div
              key={fighter.id}
              className="bg-white rounded-lg shadow-lg overflow-hidden hover:shadow-xl transition-shadow"
            >
              {/* Фото бойца */}
              <div className="h-48 bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center">
                {fighter.image_url ? (
                  <img
                    src={fighter.image_url}
                    alt={fighter.name}
                    className="w-full h-full object-cover"
                  />
                ) : (
                  <div className="text-white text-6xl">🥊</div>
                )}
              </div>

              {/* Информация о бойце */}
              <div className="p-4">
                <h3 className="font-bold text-xl text-gray-900 mb-2">
                  {fighter.name_ru || fighter.name}
                </h3>
                {fighter.name_en && fighter.name_en !== fighter.name_ru && (
                  <div className="text-sm text-gray-500 mb-1">{fighter.name_en}</div>
                )}
                
                <div className="space-y-2 text-sm text-gray-600">
                  <div className="flex items-center">
                    <span className="font-medium">Страна:</span>
                    <span className="ml-2">{fighter.country || 'Не указана'}</span>
                  </div>
                  
                  <div className="flex items-center">
                    <span className="font-medium">Категория:</span>
                    <span className="ml-2">{getWeightClassName(fighter.weight_class_id)}</span>
                  </div>
                  
                  <div className="flex items-center">
                    <span className="font-medium">Рекорд:</span>
                    <span className="ml-2 font-bold text-blue-600">
                      {fighter.wins}-{fighter.losses}-{fighter.draws}
                    </span>
                  </div>
                  
                  {fighter.height && (
                    <div className="flex items-center">
                      <span className="font-medium">Рост:</span>
                      <span className="ml-2">{fighter.height} см</span>
                    </div>
                  )}
                  
                  {fighter.reach && (
                    <div className="flex items-center">
                      <span className="font-medium">Размах рук:</span>
                      <span className="ml-2">{fighter.reach} см</span>
                    </div>
                  )}
                </div>

                {/* Кнопка подробнее */}
                <button className="w-full mt-4 bg-blue-600 text-white py-2 px-4 rounded-lg hover:bg-blue-700 transition-colors">
                  Подробнее
                </button>
              </div>
            </div>
          ))}
        </div>

        {filteredFighters.length === 0 && (
          <div className="text-center py-12">
            <div className="text-6xl mb-4">🔍</div>
            <h3 className="text-xl font-semibold text-gray-600 mb-2">
              Бойцы не найдены
            </h3>
            <p className="text-gray-500">
              Попробуйте изменить параметры поиска
            </p>
          </div>
        )}
      </div>
    </div>
  )
}

export default FightersPage
