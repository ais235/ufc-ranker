import axios from 'axios'
import { Fighter, WeightClass, Ranking, FighterDetail, UpcomingFight, Comparison, Event, Fight, FightStats, FighterStatsSummary } from '../types'

const API_BASE_URL = '/api'

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

export const api = {
  // Бойцы
  getFighters: async (params?: {
    skip?: number
    limit?: number
    search?: string
    country?: string
  }): Promise<Fighter[]> => {
    const response = await apiClient.get('/fighters', { params })
    return response.data
  },

  getFighter: async (id: number): Promise<FighterDetail> => {
    const response = await apiClient.get(`/fighters/${id}`)
    return response.data
  },

  // Весовые категории
  getWeightClasses: async (): Promise<WeightClass[]> => {
    const response = await apiClient.get('/weight-classes')
    return response.data
  },

  // Рейтинги
  getRankings: async (classId?: number): Promise<Ranking[]> => {
    const url = classId ? `/rankings/${classId}` : '/rankings'
    const response = await apiClient.get(url)
    return response.data
  },

  getChampion: async (classId: number): Promise<Ranking | null> => {
    const response = await apiClient.get(`/rankings/${classId}/champion`)
    return response.data
  },

  // Сравнение
  compareFighters: async (fighter1Id: number, fighter2Id: number): Promise<Comparison> => {
    const response = await apiClient.get(`/compare/${fighter1Id}/${fighter2Id}`)
    return response.data
  },

  // Предстоящие бои
  getUpcomingFights: async (params?: {
    limit?: number
    main_event_only?: boolean
  }): Promise<UpcomingFight[]> => {
    const response = await apiClient.get('/upcoming-fights', { params })
    return response.data
  },

  // Статистика
  getStats: async () => {
    const response = await apiClient.get('/stats')
    return response.data
  },

  // События
  getEvents: async (params?: {
    skip?: number
    limit?: number
    upcoming_only?: boolean
  }): Promise<Event[]> => {
    const response = await apiClient.get('/events', { params })
    return response.data
  },

  getEvent: async (id: number): Promise<Event> => {
    const response = await apiClient.get(`/events/${id}`)
    return response.data
  },

  // Бои
  getFights: async (params?: {
    skip?: number
    limit?: number
    fighter_id?: number
    weight_class_id?: number
  }): Promise<Fight[]> => {
    const response = await apiClient.get('/fights', { params })
    return response.data
  },

  getFight: async (id: number): Promise<Fight> => {
    const response = await apiClient.get(`/fights/${id}`)
    return response.data
  },

  getFightStats: async (fightId: number): Promise<FightStats[]> => {
    const response = await apiClient.get(`/fights/${fightId}/stats`)
    return response.data
  },

  // Статистика бойцов
  getFighterStats: async (fighterId: number): Promise<FighterStatsSummary> => {
    const response = await apiClient.get(`/fighters/${fighterId}/stats`)
    return response.data
  },

  getFighterFights: async (fighterId: number, limit?: number): Promise<Fight[]> => {
    const response = await apiClient.get(`/fighters/${fighterId}/fights`, { 
      params: { limit } 
    })
    return response.data
  },

  // Обновление данных ufc.stats
  refreshUFCStats: async () => {
    const response = await apiClient.post('/refresh-ufc-stats')
    return response.data
  },
}
