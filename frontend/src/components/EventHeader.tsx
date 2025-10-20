import React from 'react'
import { Event, Fight } from '../types'

interface EventHeaderProps {
  event: Event
}

const EventHeader: React.FC<EventHeaderProps> = ({ event }) => {
  return (
    <div className="bg-gradient-to-r from-yellow-400 to-yellow-500 text-black p-8 rounded-2xl mb-8 text-center shadow-2xl">
      <h1 className="text-4xl md:text-5xl font-bold mb-4 drop-shadow-lg">
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
  )
}

export default EventHeader
