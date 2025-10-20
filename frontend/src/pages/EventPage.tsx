import React, { useState, useEffect } from 'react'
import { useParams, Link } from 'react-router-dom'
import Layout from '../components/Layout'
import { api } from '../services/api'
import { Event, Fight } from '../types'

const EventPage: React.FC = () => {
  const { eventId } = useParams<{ eventId: string }>()
  const [event, setEvent] = useState<Event | null>(null)
  const [fights, setFights] = useState<Fight[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (eventId) {
      loadEventData(eventId)
    }
  }, [eventId])

  const loadEventData = async (eventIdentifier: string) => {
    try {
      setLoading(true)
      setError(null)

      // Сначала пытаемся найти событие по ID (если это число)
      let eventData: Event | null = null
      
      if (!isNaN(Number(eventIdentifier))) {
        // Если это число, ищем по ID
        eventData = await api.getEvent(Number(eventIdentifier))
      } else {
        // Если это строка, ищем по названию
        const events = await api.getEvents({ limit: 100 })
        eventData = events.find(e => 
          e.name.toLowerCase().replace(/\s+/g, '_').replace(/[^\w\-_]/g, '') === eventIdentifier.toLowerCase()
        ) || null
      }

      if (!eventData) {
        setError('Событие не найдено')
        return
      }

      setEvent(eventData)

      // Загружаем бои для этого события
      const fightsData = await api.getFights({ event_id: eventData.id })
      setFights(fightsData)

    } catch (error) {
      console.error('Ошибка загрузки события:', error)
      setError('Ошибка загрузки данных события')
    } finally {
      setLoading(false)
    }
  }

  const formatDate = (dateString: string | undefined) => {
    if (!dateString) return 'Дата TBA'
    return new Date(dateString).toLocaleDateString('ru-RU', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    })
  }

  const getResultColor = (fight: Fight) => {
    if (fight.winner_name) return 'text-green-400'
    if (fight.is_draw === 'Draw') return 'text-yellow-400'
    if (fight.is_nc === 'No Contest') return 'text-gray-400'
    return 'text-white'
  }

  const getResultText = (fight: Fight) => {
    if (fight.winner_name) return `Победитель: ${fight.winner_name}`
    if (fight.is_draw === 'Draw') return 'Ничья'
    if (fight.is_nc === 'No Contest') return 'Не состоялся'
    return 'Результат неизвестен'
  }

  const getCardTypeLabel = (cardType: string | undefined) => {
    if (!cardType) return ''
    
    switch (cardType.toLowerCase()) {
      case 'main card':
        return 'Основная карта'
      case 'preliminary card':
        return 'Предварительная карта'
      case 'early preliminary card':
        return 'Ранняя предварительная карта'
      default:
        return cardType
    }
  }

  const getCardTypeColor = (cardType: string | undefined) => {
    if (!cardType) return 'bg-gray-600'
    
    switch (cardType.toLowerCase()) {
      case 'main card':
        return 'bg-red-600'
      case 'preliminary card':
        return 'bg-blue-600'
      case 'early preliminary card':
        return 'bg-green-600'
      default:
        return 'bg-gray-600'
    }
  }

  const getFighterPhotoClass = (fight: Fight, fighterNumber: 1 | 2) => {
    if (!fight.winner_name) return 'fighter-photo-placeholder'
    
    const fighterName = fighterNumber === 1 ? fight.fighter1_name : fight.fighter2_name
    if (fighterName === fight.winner_name) {
      return 'fighter-photo-winner'
    } else {
      return 'fighter-photo-loser'
    }
  }

  if (loading) {
    return (
      <Layout>
        <div className="flex items-center justify-center min-h-96">
          <div className="text-center">
            <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-yellow-400 mx-auto"></div>
            <p className="mt-4 text-white text-xl">Загрузка события...</p>
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
            <Link to="/events" className="mt-4 btn-primary inline-block">
              Вернуться к событиям
            </Link>
          </div>
        </div>
      </Layout>
    )
  }

  if (!event) {
    return (
      <Layout>
        <div className="flex items-center justify-center min-h-96">
          <div className="text-center">
            <h1 className="text-4xl font-bold text-white mb-4">Событие не найдено</h1>
            <Link to="/events" className="mt-4 btn-primary inline-block">
              Вернуться к событиям
            </Link>
          </div>
        </div>
      </Layout>
    )
  }

  return (
    <Layout>
      <div className="container mx-auto px-4 py-8">
        {/* Заголовок события */}
        <div className="bg-gradient-to-r from-yellow-400 to-yellow-500 text-black p-8 rounded-2xl mb-8 text-center shadow-2xl">
          <h1 className="text-4xl md:text-5xl font-bold mb-4 text-shadow-lg">
            {event.name}
          </h1>
          <div className="text-xl md:text-2xl font-semibold mb-6 opacity-80">
            {event.event_number || 'UFC Event'}
          </div>
          <div className="text-lg md:text-xl opacity-70">
            {event.event_type || 'Mixed Martial Arts'}
          </div>
          {event.is_upcoming && (
            <div className="bg-red-500 text-white px-4 py-2 rounded-full text-sm font-bold mt-4 inline-block">
              Предстоящее событие
            </div>
          )}
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 mb-8">
          {/* Постер события */}
          <div className="lg:col-span-1">
            <div className="bg-white bg-opacity-10 backdrop-blur-lg border border-white border-opacity-20 p-6 rounded-2xl text-center">
              <div className="w-full max-w-xs h-96 bg-gradient-to-br from-gray-700 to-gray-800 rounded-xl mx-auto mb-6 flex items-center justify-center shadow-2xl">
                <div className="text-center">
                  <div className="text-6xl mb-4">🥊</div>
                  <p className="text-gray-300 text-lg">Постер события</p>
                </div>
              </div>
              <h3 className="text-xl font-semibold text-yellow-400 mb-2">
                {event.name}
              </h3>
              <p className="text-gray-300">
                {formatDate(event.event_date)}
              </p>
            </div>
          </div>
          
          {/* Информация о событии */}
          <div className="lg:col-span-2">
            <div className="bg-white bg-opacity-10 backdrop-blur-lg border border-white border-opacity-20 p-6 rounded-2xl">
              <h2 className="text-2xl font-bold text-yellow-400 mb-6 border-b-2 border-yellow-400 pb-3">
                📅 Информация о событии
              </h2>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
                <div className="space-y-4">
                  <div>
                    <p className="text-gray-300 text-sm mb-1">Дата/время:</p>
                    <p className="text-white font-medium">{formatDate(event.event_date)}</p>
                  </div>
                  
                  <div>
                    <p className="text-gray-300 text-sm mb-1">Местоположение:</p>
                    <p className="text-white font-medium">{event.location || 'Не указано'}</p>
                  </div>
                  
                  <div>
                    <p className="text-gray-300 text-sm mb-1">Место проведения:</p>
                    <p className="text-white font-medium">{event.venue || 'Не указана'}</p>
                  </div>
                </div>
                
                <div className="space-y-4">
                  <div>
                    <p className="text-gray-300 text-sm mb-1">Посещаемость:</p>
                    <p className="text-white font-medium">
                      {event.attendance ? event.attendance.toLocaleString() : 'Не указано'}
                    </p>
                  </div>
                  
                  <div>
                    <p className="text-gray-300 text-sm mb-1">Доход от билетов:</p>
                    <p className="text-white font-medium">{event.gate_revenue || 'Не указан'}</p>
                  </div>
                  
                  <div>
                    <p className="text-gray-300 text-sm mb-1">Количество боёв:</p>
                    <p className="text-white font-medium">{fights.length}</p>
                  </div>
                </div>
              </div>

              {/* Дополнительная информация */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="bg-white bg-opacity-5 p-4 rounded-xl">
                  <h4 className="text-yellow-400 font-semibold mb-3">📺 Телеведущие</h4>
                  <ul className="text-gray-300 text-sm space-y-1">
                    <li>Джо Роган</li>
                    <li>Дэниел Кормье</li>
                    <li>Джон Аники</li>
                    <li>Пол Фелдер</li>
                  </ul>
                </div>
                
                <div className="bg-white bg-opacity-5 p-4 rounded-xl">
                  <h4 className="text-yellow-400 font-semibold mb-3">🎙️ Комментаторы</h4>
                  <ul className="text-gray-300 text-sm space-y-1">
                    <li>Джо Роган</li>
                    <li>Дэниел Кормье</li>
                  </ul>
                </div>
                
                <div className="bg-white bg-opacity-5 p-4 rounded-xl">
                  <h4 className="text-yellow-400 font-semibold mb-3">🎤 Интервью после боя</h4>
                  <ul className="text-gray-300 text-sm space-y-1">
                    <li>Интервью с победителем</li>
                    <li>Пресс-конференция</li>
                  </ul>
                </div>
              </div>
            </div>
          </div>
        </div>
        
        {/* Карточки боев */}
        <div className="bg-white bg-opacity-10 backdrop-blur-lg border border-white border-opacity-20 p-6 rounded-2xl">
          <h2 className="text-2xl font-bold text-yellow-400 mb-6 border-b-2 border-yellow-400 pb-3">
            🥊 Бои события
          </h2>
          
          {fights.length > 0 ? (
            <div className="space-y-6">
              {fights.map((fight) => (
                <div key={fight.id} className="bg-white bg-opacity-5 p-6 rounded-xl">
                  {/* Заголовок карты */}
                  {fight.card_type && (
                    <div className={`inline-block px-3 py-1 rounded-full text-sm font-semibold mb-4 ${getCardTypeColor(fight.card_type)}`}>
                      {getCardTypeLabel(fight.card_type)}
                      {fight.fight_order && (
                        <span className="ml-2 text-gray-300">#{fight.fight_order}</span>
                      )}
                    </div>
                  )}
                  
                  <div className="mb-4">
                    <div className="flex justify-between items-center mb-2">
                      <h3 className="text-lg font-semibold text-yellow-400">
                        {fight.weight_class}
                      </h3>
                      {fight.is_title_fight && (
                        <span className="bg-yellow-500 text-black px-3 py-1 rounded-full text-xs font-bold mr-2">
                          Титульный бой
                        </span>
                      )}
                      {fight.is_main_event && (
                        <span className="bg-red-500 text-white px-3 py-1 rounded-full text-xs font-bold">
                          Главное событие
                        </span>
                      )}
                    </div>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-3 gap-6 items-center">
                    {/* Боец 1 */}
                    <div className="text-center">
                      <div className={`w-20 h-24 mx-auto mb-3 rounded-lg flex items-center justify-center text-xs text-gray-300 border-2 ${getFighterPhotoClass(fight, 1) === 'fighter-photo-winner' ? 'border-green-400 bg-green-400 bg-opacity-20' : getFighterPhotoClass(fight, 1) === 'fighter-photo-loser' ? 'border-red-400 bg-red-400 bg-opacity-20' : 'border-gray-500'}`}>
                        Фото
                      </div>
                      <div className="font-bold text-white text-lg mb-1">
                        {fight.fighter1_name}
                      </div>
                      <div className="text-yellow-400 text-sm italic mb-1">
                        "{fight.fighter1_name}"
                      </div>
                      <div className="text-gray-300 text-sm mb-1">
                        {fight.fighter1_country || 'Не указана'}
                      </div>
                      <div className="text-gray-400 text-xs">
                        {fight.fighter1_record || '0-0-0-0'}
                      </div>
                    </div>

                    {/* VS */}
                    <div className="text-center">
                      <div className="text-2xl font-bold text-yellow-400 mb-4">VS</div>
                      
                      {/* Результат боя */}
                      <div className="bg-white bg-opacity-10 p-4 rounded-lg text-center">
                        <div className={`font-bold text-lg mb-2 ${getResultColor(fight)}`}>
                          {getResultText(fight)}
                        </div>
                        <div className="text-gray-300 text-sm">
                          {fight.method && `Способ: ${fight.method}`}
                        </div>
                        {fight.judges_score && (
                          <div className="text-gray-300 text-sm">
                            Судьи: {fight.judges_score}
                          </div>
                        )}
                        {fight.round && (
                          <div className="text-gray-300 text-sm">
                            Раунд: {fight.round}
                          </div>
                        )}
                        {fight.time && (
                          <div className="text-gray-300 text-sm">
                            Время: {fight.time}
                          </div>
                        )}
                      </div>
                    </div>

                    {/* Боец 2 */}
                    <div className="text-center">
                      <div className={`w-20 h-24 mx-auto mb-3 rounded-lg flex items-center justify-center text-xs text-gray-300 border-2 ${getFighterPhotoClass(fight, 2) === 'fighter-photo-winner' ? 'border-green-400 bg-green-400 bg-opacity-20' : getFighterPhotoClass(fight, 2) === 'fighter-photo-loser' ? 'border-red-400 bg-red-400 bg-opacity-20' : 'border-gray-500'}`}>
                        Фото
                      </div>
                      <div className="font-bold text-white text-lg mb-1">
                        {fight.fighter2_name}
                      </div>
                      <div className="text-yellow-400 text-sm italic mb-1">
                        "{fight.fighter2_name}"
                      </div>
                      <div className="text-gray-300 text-sm mb-1">
                        {fight.fighter2_country || 'Не указана'}
                      </div>
                      <div className="text-gray-400 text-xs">
                        {fight.fighter2_record || '0-0-0-0'}
                      </div>
                    </div>
                  </div>

                  {fight.method_details && (
                    <div className="mt-4 p-3 bg-gray-800 bg-opacity-50 rounded-lg">
                      <p className="text-gray-300 text-sm">{fight.method_details}</p>
                    </div>
                  )}
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-12">
              <div className="text-6xl mb-4">🥊</div>
              <p className="text-gray-300 text-xl">Бои для этого события не найдены</p>
            </div>
          )}
        </div>
      </div>
    </Layout>
  )
}

export default EventPage
