import React from 'react'

interface StatsOverviewProps {
  stats: {
    total_fighters: number
    total_events: number
    total_fights: number
    total_weight_classes: number
  } | null
}

const StatsOverview: React.FC<StatsOverviewProps> = ({ stats }) => {
  if (!stats) return null

  return (
    <div className="bg-white rounded-lg shadow-lg p-8 mb-12">
      <h2 className="text-3xl font-bold text-gray-900 mb-6 text-center">
        Статистика UFC
      </h2>
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 md:gap-6">
        <div className="text-center">
          <div className="text-4xl font-bold text-blue-600">{stats.total_fighters}</div>
          <div className="text-gray-600 text-lg">Бойцов</div>
        </div>
        <div className="text-center">
          <div className="text-4xl font-bold text-green-600">{stats.total_events}</div>
          <div className="text-gray-600 text-lg">Событий</div>
        </div>
        <div className="text-center">
          <div className="text-4xl font-bold text-purple-600">{stats.total_fights}</div>
          <div className="text-gray-600 text-lg">Боев</div>
        </div>
        <div className="text-center">
          <div className="text-4xl font-bold text-orange-600">{stats.total_weight_classes}</div>
          <div className="text-gray-600 text-lg">Весовых категорий</div>
        </div>
      </div>
    </div>
  )
}

export default StatsOverview
