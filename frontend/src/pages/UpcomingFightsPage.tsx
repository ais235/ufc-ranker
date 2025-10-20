import React, { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { Calendar, MapPin, Trophy, Clock } from 'lucide-react'
import { api } from '../services/api'
import { UpcomingFight } from '../types'

const UpcomingFightsPage: React.FC = () => {
  const [fights, setFights] = useState<UpcomingFight[]>([])
  const [loading, setLoading] = useState(true)
  const [mainEventOnly, setMainEventOnly] = useState(false)

  useEffect(() => {
    loadFights()
  }, [mainEventOnly])

  const loadFights = async () => {
    try {
      setLoading(true)
      const fightsData = await api.getUpcomingFights({
        limit: 50,
        main_event_only: mainEventOnly
      })
      setFights(fightsData)
    } catch (error) {
      console.error('Ошибка загрузки боев:', error)
    } finally {
      setLoading(false)
    }
  }

  const formatDate = (dateString: string) => {
    try {
      const date = new Date(dateString)
      return date.toLocaleDateString('ru-RU', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
      })
    } catch {
      return dateString
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-ufc-blue mx-auto mb-4"></div>
          <p className="text-gray-600">Загрузка предстоящих боев...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="max-w-6xl mx-auto">
      {/* Заголовок */}
      <div className="text-center mb-8">
        <h1 className="text-4xl font-bold text-gray-900 mb-4">
          Предстоящие карды UFC
        </h1>
        <p className="text-lg text-gray-600">
          Ближайшие события и бои в UFC
        </p>
      </div>

      {/* Фильтры */}
      <div className="mb-8">
        <div className="flex items-center justify-center space-x-4">
          <label className="flex items-center space-x-2">
            <input
              type="checkbox"
              checked={mainEventOnly}
              onChange={(e) => setMainEventOnly(e.target.checked)}
              className="rounded border-gray-300 text-ufc-blue focus:ring-ufc-blue"
            />
            <span className="text-sm font-medium text-gray-700">
              Только главные бои
            </span>
          </label>
        </div>
      </div>

      {/* Список боев */}
      {fights.length === 0 ? (
        <div className="text-center py-12">
          <Calendar className="h-16 w-16 text-gray-400 mx-auto mb-4" />
          <h3 className="text-xl font-semibold text-gray-900 mb-2">
            Нет предстоящих боев
          </h3>
          <p className="text-gray-600">
            Информация о предстоящих боях будет добавлена позже
          </p>
        </div>
      ) : (
        <div className="space-y-6">
          {fights.map((fight) => (
            <div
              key={fight.id}
              className={`card p-6 ${
                fight.is_main_event ? 'border-2 border-ufc-gold bg-gradient-to-r from-ufc-gold/5 to-transparent' : ''
              }`}
            >
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center space-x-2">
                  {fight.is_main_event && (
                    <Trophy className="h-5 w-5 text-ufc-gold" />
                  )}
                  <h3 className="text-lg font-semibold text-gray-900">
                    {fight.weight_class.name_ru}
                  </h3>
                  {fight.is_title_fight && (
                    <span className="px-2 py-1 bg-ufc-gold text-ufc-dark text-xs font-bold rounded">
                      ТИТУЛЬНЫЙ БОЙ
                    </span>
                  )}
                </div>
                {fight.is_main_event && (
                  <span className="px-3 py-1 bg-ufc-gold text-ufc-dark text-sm font-bold rounded">
                    ГЛАВНЫЙ БОЙ
                  </span>
                )}
              </div>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                {/* Боец 1 */}
                <div className="text-center">
                  <div className="relative mb-3">
                    {fight.fighter1.image_url ? (
                      <img
                        src={fight.fighter1.image_url}
                        alt={fight.fighter1.name_ru}
                        className="w-24 h-28 object-cover rounded-lg mx-auto border-2 border-gray-200"
                      />
                    ) : (
                      <div className="w-24 h-28 bg-gray-200 rounded-lg mx-auto flex items-center justify-center">
                        <span className="text-gray-400 text-sm">Нет фото</span>
                      </div>
                    )}
                  </div>
                  <h4 className="font-bold text-gray-900">
                    {fight.fighter1.name_ru}
                  </h4>
                  {fight.fighter1.nickname && (
                    <p className="text-sm text-ufc-gold">
                      "{fight.fighter1.nickname}"
                    </p>
                  )}
                  {fight.fighter1.country && (
                    <p className="text-xs text-gray-600">
                      {fight.fighter1.country}
                    </p>
                  )}
                </div>

                {/* VS */}
                <div className="flex items-center justify-center">
                  <div className="text-center">
                    <div className="text-2xl font-bold text-ufc-blue mb-2">VS</div>
                    <div className="text-sm text-gray-600">
                      {fight.weight_class.name_ru}
                    </div>
                  </div>
                </div>

                {/* Боец 2 */}
                <div className="text-center">
                  <div className="relative mb-3">
                    {fight.fighter2.image_url ? (
                      <img
                        src={fight.fighter2.image_url}
                        alt={fight.fighter2.name_ru}
                        className="w-24 h-28 object-cover rounded-lg mx-auto border-2 border-gray-200"
                      />
                    ) : (
                      <div className="w-24 h-28 bg-gray-200 rounded-lg mx-auto flex items-center justify-center">
                        <span className="text-gray-400 text-sm">Нет фото</span>
                      </div>
                    )}
                  </div>
                  <h4 className="font-bold text-gray-900">
                    {fight.fighter2.name_ru}
                  </h4>
                  {fight.fighter2.nickname && (
                    <p className="text-sm text-ufc-gold">
                      "{fight.fighter2.nickname}"
                    </p>
                  )}
                  {fight.fighter2.country && (
                    <p className="text-xs text-gray-600">
                      {fight.fighter2.country}
                    </p>
                  )}
                </div>
              </div>

              {/* Дополнительная информация */}
              <div className="mt-4 pt-4 border-t border-gray-200">
                <div className="flex items-center justify-center space-x-6 text-sm text-gray-600">
                  <div className="flex items-center space-x-1">
                    <Calendar className="h-4 w-4" />
                    <span>Дата уточняется</span>
                  </div>
                  <div className="flex items-center space-x-1">
                    <MapPin className="h-4 w-4" />
                    <span>Место уточняется</span>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

export default UpcomingFightsPage




























