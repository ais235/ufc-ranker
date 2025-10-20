import React, { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import Layout from '../components/Layout'
import { api } from '../services/api'
import { Event } from '../types'

const EventsPage: React.FC = () => {
  const [events, setEvents] = useState<Event[]>([])
  const [upcomingEvents, setUpcomingEvents] = useState<Event[]>([])
  const [pastEvents, setPastEvents] = useState<Event[]>([])
  const [loading, setLoading] = useState(true)
  const [activeTab, setActiveTab] = useState<'all' | 'upcoming' | 'past'>('all')

  useEffect(() => {
    loadEvents()
  }, [])

  const loadEvents = async () => {
    try {
      const [allEvents, upcomingData] = await Promise.all([
        api.getEvents({ limit: 50 }),
        api.getEvents({ upcoming_only: true, limit: 20 })
      ])
      
      setEvents(allEvents)
      setUpcomingEvents(upcomingData)
      setPastEvents(allEvents.filter(event => !event.is_upcoming))
    } catch (error) {
      console.error('Ошибка загрузки событий:', error)
    } finally {
      setLoading(false)
    }
  }

  const getEventUrl = (event: Event) => {
    const name = event.name.replace(/\s+/g, '_').replace(/[^\w\-_]/g, '')
    return `/events/${name}`
  }

  const formatDate = (dateString: string | undefined) => {
    if (!dateString) return 'Дата TBA'
    return new Date(dateString).toLocaleDateString('ru-RU', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    })
  }

  const renderEvents = (eventsList: Event[]) => {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {eventsList.map((event) => (
          <div
            key={event.id}
            className="bg-gray-800 bg-opacity-50 rounded-lg p-6 border border-gray-700 hover:bg-opacity-70 transition-all"
          >
            {/* Постер события */}
            <div className="w-full h-48 bg-gradient-to-br from-gray-700 to-gray-800 rounded-lg mb-4 flex items-center justify-center">
              <div className="text-center">
                <div className="text-6xl mb-2">🥊</div>
                <p className="text-gray-300 text-sm">Постер события</p>
              </div>
            </div>

            {/* Информация о событии */}
            <div className="text-center">
              <h3 className="text-xl font-bold text-white mb-2 line-clamp-2">
                {event.name}
              </h3>
              
              <div className="space-y-2 text-sm mb-4">
                <div className="flex justify-between">
                  <span className="text-gray-400">Дата:</span>
                  <span className="text-white">{formatDate(event.event_date)}</span>
                </div>
                
                <div className="flex justify-between">
                  <span className="text-gray-400">Место:</span>
                  <span className="text-white">{event.location || 'TBA'}</span>
                </div>
                
                <div className="flex justify-between">
                  <span className="text-gray-400">Арена:</span>
                  <span className="text-white">{event.venue || 'TBA'}</span>
                </div>
                
                {event.attendance && (
                  <div className="flex justify-between">
                    <span className="text-gray-400">Зрители:</span>
                    <span className="text-white">{event.attendance.toLocaleString()}</span>
                  </div>
                )}
              </div>

              {event.is_upcoming && (
                <div className="bg-red-500 text-white px-3 py-1 rounded-full text-xs font-bold mb-4 inline-block">
                  Предстоящее событие
                </div>
              )}

              <Link
                to={getEventUrl(event)}
                className="w-full btn-primary text-center inline-block"
              >
                Подробнее
              </Link>
            </div>
          </div>
        ))}
      </div>
    )
  }

  if (loading) {
    return (
      <Layout>
        <div className="flex items-center justify-center min-h-96">
          <div className="text-center">
            <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-yellow-400 mx-auto"></div>
            <p className="mt-4 text-white text-xl">Загрузка событий...</p>
          </div>
        </div>
      </Layout>
    )
  }

  return (
    <Layout>
      {/* Заголовок */}
      <div className="card text-center mb-8">
        <h1 className="section-title">📅 События UFC</h1>
        <p className="text-gray-300 text-lg">
          Предстоящие и прошедшие события UFC
        </p>
      </div>

      {/* Табы */}
      <div className="card mb-8">
        <div className="flex flex-wrap justify-center gap-4">
          <button
            onClick={() => setActiveTab('all')}
            className={`px-6 py-3 rounded-lg font-semibold transition-all ${
              activeTab === 'all'
                ? 'bg-yellow-400 text-black'
                : 'bg-gray-800 text-white hover:bg-gray-700'
            }`}
          >
            Все события ({events.length})
          </button>
          <button
            onClick={() => setActiveTab('upcoming')}
            className={`px-6 py-3 rounded-lg font-semibold transition-all ${
              activeTab === 'upcoming'
                ? 'bg-yellow-400 text-black'
                : 'bg-gray-800 text-white hover:bg-gray-700'
            }`}
          >
            Предстоящие ({upcomingEvents.length})
          </button>
          <button
            onClick={() => setActiveTab('past')}
            className={`px-6 py-3 rounded-lg font-semibold transition-all ${
              activeTab === 'past'
                ? 'bg-yellow-400 text-black'
                : 'bg-gray-800 text-white hover:bg-gray-700'
            }`}
          >
            Прошедшие ({pastEvents.length})
          </button>
        </div>
      </div>

      {/* Список событий */}
      <div className="card">
        {activeTab === 'all' && renderEvents(events)}
        {activeTab === 'upcoming' && renderEvents(upcomingEvents)}
        {activeTab === 'past' && renderEvents(pastEvents)}
        
        {((activeTab === 'all' && events.length === 0) ||
          (activeTab === 'upcoming' && upcomingEvents.length === 0) ||
          (activeTab === 'past' && pastEvents.length === 0)) && (
          <div className="text-center py-12">
            <div className="text-6xl mb-4">📅</div>
            <p className="text-gray-300 text-xl">События не найдены</p>
          </div>
        )}
      </div>
    </Layout>
  )
}

export default EventsPage
