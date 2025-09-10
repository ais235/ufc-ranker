import React, { useState, useEffect } from 'react'
import { api } from '../services/api'
import { Fighter, WeightClass, Ranking } from '../types'

const RankingsPage: React.FC = () => {
  const [weightClasses, setWeightClasses] = useState<WeightClass[]>([])
  const [rankings, setRankings] = useState<Ranking[]>([])
  const [selectedWeightClass, setSelectedWeightClass] = useState<WeightClass | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadData()
  }, [])

  const loadData = async () => {
    try {
      const [weightClassesData, rankingsData] = await Promise.all([
        api.getWeightClasses(),
        api.getRankings()
      ])
      setWeightClasses(weightClassesData)
      setRankings(rankingsData)
      
      if (weightClassesData.length > 0) {
        setSelectedWeightClass(weightClassesData[0])
      }
    } catch (error) {
      console.error('Ошибка загрузки данных:', error)
    } finally {
      setLoading(false)
    }
  }

  const getRankingsForWeightClass = (weightClassId: number) => {
    return rankings
      .filter(ranking => ranking.weight_class_id === weightClassId)
      .sort((a, b) => a.position - b.position)
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-100 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Загрузка рейтингов...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-100">
      <div className="container mx-auto px-4 py-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-8 text-center">
          🥊 Рейтинги UFC
        </h1>

        {/* Весовые категории */}
        <div className="mb-8">
          <h2 className="text-xl font-semibold text-gray-800 mb-4">Выберите весовую категорию:</h2>
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3">
            {weightClasses.map((weightClass) => (
              <button
                key={weightClass.id}
                onClick={() => setSelectedWeightClass(weightClass)}
                className={`p-3 rounded-lg border-2 transition-all ${
                  selectedWeightClass?.id === weightClass.id
                    ? 'border-blue-500 bg-blue-50 text-blue-700'
                    : 'border-gray-300 bg-white hover:border-gray-400'
                }`}
              >
                <div className="font-medium">{weightClass.name_ru || weightClass.name}</div>
                <div className="text-sm text-gray-600">
                  {weightClass.weight_limit || 'без ограничений'}
                </div>
              </button>
            ))}
          </div>
        </div>

        {/* Рейтинг выбранной категории */}
        {selectedWeightClass && (
          <div className="bg-white rounded-lg shadow-lg p-6">
            <h3 className="text-2xl font-bold text-gray-900 mb-6 text-center">
              {selectedWeightClass.name_ru || selectedWeightClass.name}
            </h3>
            
            <div className="space-y-3">
              {getRankingsForWeightClass(selectedWeightClass.id).map((ranking, index) => (
                <div
                  key={ranking.id}
                  className="flex items-center p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
                >
                  <div className="flex-shrink-0 w-12 h-12 bg-blue-600 text-white rounded-full flex items-center justify-center font-bold text-lg mr-4">
                    {ranking.position}
                  </div>
                  
                  <div className="flex-grow">
                    <div className="flex items-center justify-between">
                      <div>
                        <h4 className="font-semibold text-gray-900 text-lg">
                          {ranking.fighter?.name_ru || ranking.fighter?.name || 'Неизвестный боец'}
                        </h4>
                        <p className="text-gray-600">
                          {ranking.fighter?.country || 'Страна не указана'}
                        </p>
                      </div>
                      
                      <div className="text-right">
                        <div className="text-sm text-gray-500">Рекорд</div>
                        <div className="font-medium">
                          {ranking.fighter?.wins || 0}-{ranking.fighter?.losses || 0}-{ranking.fighter?.draws || 0}
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              ))}
              
              {getRankingsForWeightClass(selectedWeightClass.id).length === 0 && (
                <div className="text-center py-8 text-gray-500">
                  <p>Рейтинги для этой весовой категории пока не загружены</p>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default RankingsPage
