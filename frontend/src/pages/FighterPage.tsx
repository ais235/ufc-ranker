import React, { useState, useEffect } from 'react'
import { useParams, Link } from 'react-router-dom'
import { ArrowLeft, Trophy, MapPin, Calendar, Ruler, Weight, Target } from 'lucide-react'
import { api } from '../services/api'
import { FighterDetail } from '../types'

const FighterPage: React.FC = () => {
  const { id } = useParams<{ id: string }>()
  const [fighter, setFighter] = useState<FighterDetail | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (id) {
      loadFighter(parseInt(id))
    }
  }, [id])

  const loadFighter = async (fighterId: number) => {
    try {
      setLoading(true)
      const fighterData = await api.getFighter(fighterId)
      setFighter(fighterData)
    } catch (error) {
      console.error('Ошибка загрузки бойца:', error)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-ufc-blue mx-auto mb-4"></div>
          <p className="text-gray-600">Загрузка...</p>
        </div>
      </div>
    )
  }

  if (!fighter) {
    return (
      <div className="text-center py-12">
        <h1 className="text-2xl font-bold text-gray-900 mb-4">Боец не найден</h1>
        <Link to="/" className="btn btn-primary">
          <ArrowLeft className="h-4 w-4 mr-2" />
          Вернуться к рейтингам
        </Link>
      </div>
    )
  }

  return (
    <div className="max-w-4xl mx-auto">
      {/* Навигация */}
      <div className="mb-6">
        <Link to="/" className="btn btn-secondary">
          <ArrowLeft className="h-4 w-4 mr-2" />
          Назад к рейтингам
        </Link>
      </div>

      <div className="card p-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Фото и основная информация */}
          <div className="text-center lg:text-left">
            <div className="relative mb-6">
              {fighter.image_url ? (
                <img
                  src={fighter.image_url}
                  alt={fighter.name_ru}
                  className="w-64 h-80 object-cover rounded-lg mx-auto lg:mx-0 border-4 border-gray-200"
                />
              ) : (
                <div className="w-64 h-80 bg-gray-200 rounded-lg mx-auto lg:mx-0 flex items-center justify-center">
                  <span className="text-gray-400 text-lg">Нет фото</span>
                </div>
              )}
            </div>

            <h1 className="text-3xl font-bold text-gray-900 mb-2">
              {fighter.name_ru}
            </h1>

            {fighter.name_en && (
              <p className="text-xl text-gray-600 mb-2">
                {fighter.name_en}
              </p>
            )}

            {fighter.nickname && (
              <p className="text-lg text-ufc-gold font-medium mb-4">
                "{fighter.nickname}"
              </p>
            )}

            {fighter.country && (
              <div className="flex items-center justify-center lg:justify-start space-x-2 mb-4">
                {fighter.country_flag_url && (
                  <img
                    src={fighter.country_flag_url}
                    alt={fighter.country}
                    className="w-6 h-4 object-cover rounded"
                  />
                )}
                <span className="text-gray-600">{fighter.country}</span>
              </div>
            )}
          </div>

          {/* Физические данные */}
          <div className="space-y-6">
            <h2 className="text-2xl font-bold text-gray-900 mb-4">Физические данные</h2>
            
            <div className="grid grid-cols-1 gap-4">
              {fighter.height && (
                <div className="flex items-center space-x-3 p-3 bg-gray-50 rounded-lg">
                  <Ruler className="h-5 w-5 text-ufc-blue" />
                  <div>
                    <p className="text-sm text-gray-600">Рост</p>
                    <p className="text-lg font-semibold">{fighter.height} см</p>
                  </div>
                </div>
              )}

              {fighter.weight && (
                <div className="flex items-center space-x-3 p-3 bg-gray-50 rounded-lg">
                  <Weight className="h-5 w-5 text-ufc-blue" />
                  <div>
                    <p className="text-sm text-gray-600">Вес</p>
                    <p className="text-lg font-semibold">{fighter.weight} кг</p>
                  </div>
                </div>
              )}

              {fighter.reach && (
                <div className="flex items-center space-x-3 p-3 bg-gray-50 rounded-lg">
                  <Target className="h-5 w-5 text-ufc-blue" />
                  <div>
                    <p className="text-sm text-gray-600">Размах рук</p>
                    <p className="text-lg font-semibold">{fighter.reach} см</p>
                  </div>
                </div>
              )}

              {fighter.age && (
                <div className="flex items-center space-x-3 p-3 bg-gray-50 rounded-lg">
                  <Calendar className="h-5 w-5 text-ufc-blue" />
                  <div>
                    <p className="text-sm text-gray-600">Возраст</p>
                    <p className="text-lg font-semibold">{fighter.age} лет</p>
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Боевой рекорд */}
          {fighter.fight_record && (
            <div className="space-y-6">
              <h2 className="text-2xl font-bold text-gray-900 mb-4">Боевой рекорд</h2>
              
              <div className="bg-ufc-dark text-white p-6 rounded-lg">
                <div className="text-center mb-4">
                  <Trophy className="h-8 w-8 text-ufc-gold mx-auto mb-2" />
                  <p className="text-3xl font-bold">
                    {fighter.fight_record.wins}-{fighter.fight_record.losses}-{fighter.fight_record.draws}
                  </p>
                  <p className="text-sm text-gray-300">
                    {fighter.fight_record.total_fights} боев
                  </p>
                </div>

                <div className="grid grid-cols-2 gap-4 text-center">
                  <div>
                    <p className="text-2xl font-bold text-green-400">
                      {fighter.fight_record.wins}
                    </p>
                    <p className="text-sm text-gray-300">Побед</p>
                  </div>
                  <div>
                    <p className="text-2xl font-bold text-red-400">
                      {fighter.fight_record.losses}
                    </p>
                    <p className="text-sm text-gray-300">Поражений</p>
                  </div>
                  <div>
                    <p className="text-2xl font-bold text-yellow-400">
                      {fighter.fight_record.draws}
                    </p>
                    <p className="text-sm text-gray-300">Ничьих</p>
                  </div>
                  <div>
                    <p className="text-2xl font-bold text-ufc-gold">
                      {fighter.fight_record.win_percentage}%
                    </p>
                    <p className="text-sm text-gray-300">Процент побед</p>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default FighterPage
