import React from 'react'
import { FighterStatsSummary } from '../types'

interface FighterStatsCardProps {
  stats: FighterStatsSummary
}

const FighterStatsCard: React.FC<FighterStatsCardProps> = ({ stats }) => {
  const {
    fighter,
    total_fights,
    total_rounds,
    total_significant_strikes_landed,
    total_significant_strikes_attempted,
    average_significant_strikes_rate,
    total_takedowns_successful,
    total_takedowns_attempted,
    average_takedown_rate,
    total_knockdowns,
    total_submission_attempts,
    total_reversals
  } = stats

  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <div className="flex items-center mb-6">
        {fighter.image_url && (
          <img 
            src={fighter.image_url} 
            alt={fighter.name_ru}
            className="w-16 h-16 rounded-full object-cover mr-4"
          />
        )}
        <div>
          <h3 className="text-2xl font-bold text-gray-900">{fighter.name_ru}</h3>
          {fighter.name_en && (
            <p className="text-gray-600">{fighter.name_en}</p>
          )}
          {fighter.country && (
            <p className="text-sm text-gray-500">{fighter.country}</p>
          )}
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {/* Общая статистика */}
        <div className="space-y-4">
          <h4 className="text-lg font-semibold text-gray-900 border-b pb-2">
            Общая статистика
          </h4>
          <div className="space-y-2">
            <div className="flex justify-between">
              <span className="text-gray-600">Боев:</span>
              <span className="font-semibold">{total_fights}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Раундов:</span>
              <span className="font-semibold">{total_rounds}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Нокдаунов:</span>
              <span className="font-semibold text-red-600">{total_knockdowns}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Субмиссий:</span>
              <span className="font-semibold text-blue-600">{total_submission_attempts}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Реверсалов:</span>
              <span className="font-semibold text-green-600">{total_reversals}</span>
            </div>
          </div>
        </div>

        {/* Удары */}
        <div className="space-y-4">
          <h4 className="text-lg font-semibold text-gray-900 border-b pb-2">
            Удары
          </h4>
          <div className="space-y-2">
            <div className="flex justify-between">
              <span className="text-gray-600">Попали:</span>
              <span className="font-semibold">{total_significant_strikes_landed}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Попыток:</span>
              <span className="font-semibold">{total_significant_strikes_attempted}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Точность:</span>
              <span className="font-semibold text-green-600">
                {average_significant_strikes_rate.toFixed(1)}%
              </span>
            </div>
          </div>
          
          {/* Прогресс-бар точности */}
          <div className="mt-3">
            <div className="flex justify-between text-sm text-gray-600 mb-1">
              <span>Точность ударов</span>
              <span>{average_significant_strikes_rate.toFixed(1)}%</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div 
                className="bg-green-500 h-2 rounded-full transition-all duration-300"
                style={{ width: `${Math.min(average_significant_strikes_rate, 100)}%` }}
              ></div>
            </div>
          </div>
        </div>

        {/* Тейкдауны */}
        <div className="space-y-4">
          <h4 className="text-lg font-semibold text-gray-900 border-b pb-2">
            Тейкдауны
          </h4>
          <div className="space-y-2">
            <div className="flex justify-between">
              <span className="text-gray-600">Успешных:</span>
              <span className="font-semibold">{total_takedowns_successful}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Попыток:</span>
              <span className="font-semibold">{total_takedowns_attempted}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Успешность:</span>
              <span className="font-semibold text-blue-600">
                {average_takedown_rate.toFixed(1)}%
              </span>
            </div>
          </div>
          
          {/* Прогресс-бар тейкдаунов */}
          <div className="mt-3">
            <div className="flex justify-between text-sm text-gray-600 mb-1">
              <span>Успешность тейкдаунов</span>
              <span>{average_takedown_rate.toFixed(1)}%</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div 
                className="bg-blue-500 h-2 rounded-full transition-all duration-300"
                style={{ width: `${Math.min(average_takedown_rate, 100)}%` }}
              ></div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default FighterStatsCard
