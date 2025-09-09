import React, { useState, useEffect } from 'react'
import WeightClassTabs from '../components/WeightClassTabs'
import FighterCard from '../components/FighterCard'
import { api } from '../services/api'
import { WeightClass, Fighter, Ranking } from '../types'

const HomePage: React.FC = () => {
  const [weightClasses, setWeightClasses] = useState<WeightClass[]>([])
  const [activeClassId, setActiveClassId] = useState<number | null>(null)
  const [rankings, setRankings] = useState<Ranking[]>([])
  const [loading, setLoading] = useState(true)
  const [compareList, setCompareList] = useState<Fighter[]>([])

  useEffect(() => {
    loadWeightClasses()
  }, [])

  useEffect(() => {
    if (activeClassId) {
      loadRankings(activeClassId)
    }
  }, [activeClassId])

  const loadWeightClasses = async () => {
    try {
      const classes = await api.getWeightClasses()
      setWeightClasses(classes)
      if (classes.length > 0) {
        setActiveClassId(classes[0].id)
      }
    } catch (error) {
      console.error('Ошибка загрузки категорий:', error)
    } finally {
      setLoading(false)
    }
  }

  const loadRankings = async (classId: number) => {
    try {
      setLoading(true)
      const rankings = await api.getRankings(classId)
      setRankings(rankings)
    } catch (error) {
      console.error('Ошибка загрузки рейтингов:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleAddToCompare = (fighter: Fighter) => {
    if (compareList.length >= 2) {
      alert('Можно сравнить максимум 2 бойцов')
      return
    }
    
    if (compareList.find(f => f.id === fighter.id)) {
      alert('Боец уже добавлен в сравнение')
      return
    }
    
    setCompareList([...compareList, fighter])
  }

  const handleRemoveFromCompare = (fighterId: number) => {
    setCompareList(compareList.filter(f => f.id !== fighterId))
  }

  if (loading && weightClasses.length === 0) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-ufc-blue mx-auto mb-4"></div>
          <p className="text-gray-600">Загрузка...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-8">
      {/* Заголовок */}
      <div className="text-center">
        <h1 className="text-4xl font-bold text-gray-900 mb-4">
          UFC Рейтинги
        </h1>
        <p className="text-lg text-gray-600">
          Актуальные рейтинги бойцов UFC по весовым категориям
        </p>
      </div>

      {/* Список сравнения */}
      {compareList.length > 0 && (
        <div className="bg-ufc-blue text-white p-4 rounded-lg">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="font-semibold mb-2">Сравнение бойцов ({compareList.length}/2)</h3>
              <div className="flex space-x-4">
                {compareList.map(fighter => (
                  <div key={fighter.id} className="flex items-center space-x-2">
                    <span className="text-sm">{fighter.name_ru}</span>
                    <button
                      onClick={() => handleRemoveFromCompare(fighter.id)}
                      className="text-white hover:text-gray-300"
                    >
                      ×
                    </button>
                  </div>
                ))}
              </div>
            </div>
            {compareList.length === 2 && (
              <button
                onClick={() => window.location.href = '/compare'}
                className="btn btn-secondary"
              >
                Сравнить
              </button>
            )}
          </div>
        </div>
      )}

      {/* Табы весовых категорий */}
      <WeightClassTabs
        weightClasses={weightClasses}
        activeClassId={activeClassId}
        onClassChange={setActiveClassId}
      />

      {/* Рейтинги */}
      {loading ? (
        <div className="flex items-center justify-center h-32">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-ufc-blue"></div>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
          {rankings.map((ranking, index) => (
            <FighterCard
              key={ranking.fighter.id}
              fighter={ranking.fighter}
              rank={ranking.is_champion ? 'Ч' : ranking.rank_position}
              isChampion={ranking.is_champion}
              onAddToCompare={handleAddToCompare}
              showCompareButton={compareList.length < 2}
            />
          ))}
        </div>
      )}

      {!loading && rankings.length === 0 && (
        <div className="text-center py-12">
          <p className="text-gray-500 text-lg">Рейтинги не найдены</p>
        </div>
      )}
    </div>
  )
}

export default HomePage
