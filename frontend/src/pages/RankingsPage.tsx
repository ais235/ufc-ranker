import React, { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import Layout from '../components/Layout'
import { api } from '../services/api'
import { WeightClass } from '../types'

const RankingsPage: React.FC = () => {
  const [weightClasses, setWeightClasses] = useState<WeightClass[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadWeightClasses()
  }, [])

  const loadWeightClasses = async () => {
    try {
      const weightClassesData = await api.getWeightClasses()
      setWeightClasses(weightClassesData)
    } catch (error) {
      console.error('Ошибка загрузки весовых категорий:', error)
    } finally {
      setLoading(false)
    }
  }

  const getWeightClassUrl = (weightClass: WeightClass) => {
    const name = weightClass.name_en.toLowerCase().replace(/\s+/g, '_')
    return `/rankings/${name}`
  }

  if (loading) {
    return (
      <Layout>
        <div className="flex items-center justify-center min-h-96">
          <div className="text-center">
            <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-yellow-400 mx-auto"></div>
            <p className="mt-4 text-white text-xl">Загрузка весовых категорий...</p>
          </div>
        </div>
      </Layout>
    )
  }

  return (
    <Layout>
      {/* Заголовок */}
      <div className="card text-center mb-8">
        <h1 className="section-title">🥊 Рейтинги UFC</h1>
        <p className="text-gray-300 text-lg">
          Выберите весовую категорию для просмотра рейтингов
        </p>
      </div>

      {/* Весовые категории */}
      <div className="card">
        <h2 className="text-2xl font-bold text-yellow-400 mb-6 text-center">
          Весовые категории
        </h2>
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
          {weightClasses.map((weightClass) => (
            <Link
              key={weightClass.id}
              to={getWeightClassUrl(weightClass)}
              className="p-4 rounded-lg border-2 border-gray-600 bg-gray-800 bg-opacity-50 hover:border-yellow-400 hover:text-yellow-400 transition-all text-center"
            >
              <div className="font-medium text-lg">{weightClass.name_ru || weightClass.name}</div>
              <div className="text-sm text-gray-400 mt-1">
                {weightClass.weight_limit || 'без ограничений'}
              </div>
            </Link>
          ))}
        </div>
      </div>
    </Layout>
  )
}

export default RankingsPage