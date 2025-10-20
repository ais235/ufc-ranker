import React from 'react'
import { Fighter } from '../types'

interface TopFightersProps {
  fighters: Fighter[]
  onFighterClick: (fighterId: number) => void
}

const TopFighters: React.FC<TopFightersProps> = ({ fighters, onFighterClick }) => {
  return (
    <div className="bg-white rounded-lg shadow-lg p-8 mb-12">
      <h2 className="text-3xl font-bold text-gray-900 mb-6">
        🏆 Топ бойцы UFC
      </h2>
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 md:gap-6">
        {fighters.map((fighter, index) => (
          <div 
            key={fighter.id} 
            className="bg-gray-50 rounded-lg p-6 hover:shadow-md transition-shadow cursor-pointer"
            onClick={() => onFighterClick(fighter.id)}
          >
            <div className="text-center">
              <div className="w-16 h-16 bg-blue-600 text-white rounded-full flex items-center justify-center font-bold text-xl mx-auto mb-4">
                {index + 1}
              </div>
              <h3 className="font-semibold text-lg mb-2">{fighter.name}</h3>
              <p className="text-gray-600 mb-2">{fighter.country}</p>
              <div className="text-sm text-gray-500">
                {fighter.wins}-{fighter.losses}-{fighter.draws}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

export default TopFighters
