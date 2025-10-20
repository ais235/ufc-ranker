import React from 'react'
import { useNavigate } from 'react-router-dom'

const HeroSection: React.FC = () => {
  const navigate = useNavigate()

  const handleNavigate = (page: string) => {
    navigate(`/${page}`)
  }
  return (
    <div className="bg-gradient-to-r from-blue-600 to-purple-600 text-white py-12 md:py-20">
      <div className="container mx-auto px-4 text-center">
        <h1 className="text-3xl md:text-5xl font-bold mb-4 md:mb-6">
          🥊 UFC Ranker
        </h1>
        <p className="text-lg md:text-xl mb-6 md:mb-8 max-w-2xl mx-auto">
          Полная база данных UFC с рейтингами бойцов, статистикой боев и предстоящими событиями
        </p>
        <div className="flex flex-col sm:flex-row justify-center gap-4">
          <button 
            onClick={() => handleNavigate('rankings')}
            className="bg-white text-blue-600 px-6 md:px-8 py-3 rounded-lg font-semibold hover:bg-gray-100 transition-colors w-full sm:w-auto"
          >
            🥊 Рейтинги
          </button>
          <button 
            onClick={() => handleNavigate('fighters')}
            className="bg-white text-blue-600 px-6 md:px-8 py-3 rounded-lg font-semibold hover:bg-gray-100 transition-colors w-full sm:w-auto"
          >
            👊 Бойцы
          </button>
          <button 
            onClick={() => handleNavigate('events')}
            className="bg-white text-blue-600 px-6 md:px-8 py-3 rounded-lg font-semibold hover:bg-gray-100 transition-colors w-full sm:w-auto"
          >
            📅 События
          </button>
        </div>
      </div>
    </div>
  )
}

export default HeroSection
