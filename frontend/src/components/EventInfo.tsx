import React from 'react'
import { Event } from '../types'

interface EventInfoProps {
  event: Event
}

const EventInfo: React.FC<EventInfoProps> = ({ event }) => {
  return (
    <div className="bg-white bg-opacity-10 backdrop-blur-lg border border-white border-opacity-20 rounded-xl p-6">
      <h2 className="text-2xl font-bold text-yellow-400 mb-6 border-b-2 border-yellow-400 pb-3">
        Информация о событии
      </h2>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="space-y-4">
          <div>
            <p className="text-gray-300 text-sm">Дата проведения:</p>
            <p className="text-white font-medium">
              {event.event_date ? new Date(event.event_date).toLocaleDateString('ru-RU') : 'Не указана'}
            </p>
          </div>
          
          <div>
            <p className="text-gray-300 text-sm">Место проведения:</p>
            <p className="text-white font-medium">{event.location || 'Не указано'}</p>
          </div>
          
          <div>
            <p className="text-gray-300 text-sm">Арена:</p>
            <p className="text-white font-medium">{event.venue || 'Не указана'}</p>
          </div>
        </div>
        
        <div className="space-y-4">
          <div>
            <p className="text-gray-300 text-sm">Количество зрителей:</p>
            <p className="text-white font-medium">
              {event.attendance ? event.attendance.toLocaleString() : 'Не указано'}
            </p>
          </div>
          
          <div>
            <p className="text-gray-300 text-sm">Статус:</p>
            <p className="text-white font-medium">
              {event.is_upcoming ? 'Предстоящее' : 'Прошедшее'}
            </p>
          </div>
          
          <div>
            <p className="text-gray-300 text-sm">Тип события:</p>
            <p className="text-white font-medium">{event.event_type || 'UFC'}</p>
          </div>
        </div>
      </div>
      
      {event.description && (
        <div className="mt-6">
          <p className="text-gray-300 text-sm mb-2">Описание:</p>
          <p className="text-white">{event.description}</p>
        </div>
      )}
    </div>
  )
}

export default EventInfo
