import React from 'react'
import { Event } from '../types'

interface LatestEventsProps {
  events: Event[]
  onEventClick: (eventId: number) => void
}

const LatestEvents: React.FC<LatestEventsProps> = ({ events, onEventClick }) => {
  return (
    <div className="bg-white rounded-lg shadow-lg p-8 mb-12">
      <h2 className="text-3xl font-bold text-gray-900 mb-6">
        📅 Последние события
      </h2>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 md:gap-6">
        {events.map((event) => (
          <div 
            key={event.id} 
            className="border rounded-lg p-6 hover:shadow-md transition-shadow cursor-pointer"
            onClick={() => onEventClick(event.id)}
          >
            <h3 className="font-semibold text-lg mb-2">{event.name}</h3>
            <p className="text-gray-600 mb-2">{event.location}</p>
            <p className="text-sm text-gray-500">
              {new Date(event.event_date).toLocaleDateString('ru-RU')}
            </p>
            {event.is_upcoming && (
              <span className="inline-block bg-red-100 text-red-800 text-xs px-2 py-1 rounded-full mt-2">
                Предстоящее
              </span>
            )}
          </div>
        ))}
      </div>
    </div>
  )
}

export default LatestEvents
