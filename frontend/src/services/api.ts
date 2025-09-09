import axios from 'axios'
import { Fighter, WeightClass, Ranking, FighterDetail, UpcomingFight, Comparison } from '../types'

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
  getRankings: async (classId: number): Promise<Ranking[]> => {
    const response = await apiClient.get(`/rankings/${classId}`)
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
}
