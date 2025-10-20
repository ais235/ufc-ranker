import React from 'react'
import { Event, Fight } from '../types'
import EventHeader from './EventHeader'
import EventInfo from './EventInfo'
import FightCard from './FightCard'

interface EventPageProps {
  event: Event
  fights: Fight[]
  loading?: boolean
}

const EventPage: React.FC<EventPageProps> = ({ event, fights, loading = false }) => {
  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-900 to-gray-800 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-yellow-400 mx-auto"></div>
          <p className="mt-4 text-white text-xl">Загрузка события...</p>
        </div>
      </div>
    )
  }

  if (!event) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-900 to-gray-800 flex items-center justify-center">
        <div className="text-center">
          <h1 className="text-4xl font-bold text-white mb-4">Событие не найдено</h1>
          <p className="text-gray-300 text-xl">Проверьте правильность ссылки</p>
        </div>
      </div>
    )
  }

  return (
    <div>
      <EventHeader event={event} />
      
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 mb-8">
        {/* Постер события */}
        <div className="lg:col-span-1">
          <div className="card text-center">
            <div className="w-full max-w-xs h-96 bg-gradient-to-br from-gray-700 to-gray-800 rounded-lg mx-auto mb-6 flex items-center justify-center shadow-2xl">
              <div className="text-center">
                <div className="text-6xl mb-4">🥊</div>
                <p className="text-gray-300 text-lg">Постер события</p>
              </div>
            </div>
            <h3 className="text-xl font-semibold text-yellow-400 mb-2">
              {event.name}
            </h3>
            <p className="text-gray-300">
              {event.event_date ? new Date(event.event_date).toLocaleDateString('ru-RU') : 'Дата TBA'}
            </p>
          </div>
        </div>
        
        {/* Информация о событии */}
        <div className="lg:col-span-2">
          <EventInfo event={event} />
        </div>
      </div>
      
      {/* Карточки боев */}
      <div className="card">
        <h2 className="text-2xl font-bold text-yellow-400 mb-6 border-b-2 border-yellow-400 pb-3">
          Карточка боев
        </h2>
        
        {fights.length > 0 ? (
          <div className="space-y-4">
            {fights.map((fight) => (
              <FightCard key={fight.id} fight={fight} />
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
  )
}

export default EventPage
