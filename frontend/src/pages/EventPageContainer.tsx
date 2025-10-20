import React, { useState, useEffect } from 'react'
import { useParams } from 'react-router-dom'
import Layout from '../components/Layout'
import { api } from '../services/api'
import { Event, Fight } from '../types'
import EventPage from '../components/EventPage'

const EventPageContainer: React.FC = () => {
  const { id } = useParams<{ id: string }>()
  const [event, setEvent] = useState<Event | null>(null)
  const [fights, setFights] = useState<Fight[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (id) {
      loadEventData(parseInt(id))
    }
  }, [id])

  const loadEventData = async (eventId: number) => {
    try {
      setLoading(true)
      setError(null)
      
      // Загружаем данные события и боев параллельно
      const [eventData, fightsData] = await Promise.all([
        api.getEvent(eventId),
        api.getFights({ event_id: eventId })
      ])
      
      setEvent(eventData)
      setFights(fightsData)
      
    } catch (err) {
      console.error('Ошибка загрузки события:', err)
      setError('Ошибка загрузки данных события')
    } finally {
      setLoading(false)
    }
  }

  if (error) {
    return (
      <Layout>
        <div className="flex items-center justify-center min-h-96">
          <div className="text-center">
            <h1 className="text-4xl font-bold text-white mb-4">Ошибка</h1>
            <p className="text-gray-300 text-xl">{error}</p>
          </div>
        </div>
      </Layout>
    )
  }

  return (
    <Layout>
      <EventPage event={event} fights={fights} loading={loading} />
    </Layout>
  )
}

export default EventPageContainer
