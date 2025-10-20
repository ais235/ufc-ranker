import React from 'react'
import { Fight } from '../types'

interface UpcomingFightsProps {
  fights: Fight[]
  onFightClick: (fightId: number) => void
}

const UpcomingFights: React.FC<UpcomingFightsProps> = ({ fights, onFightClick }) => {
  return (
    <div className="bg-white rounded-lg shadow-lg p-8 mb-12">
      <h2 className="text-3xl font-bold text-gray-900 mb-6">
        ⚔️ Предстоящие бои
      </h2>
      <div className="space-y-4">
        {fights.map((fight) => (
          <div 
            key={fight.id} 
            className="border rounded-lg p-6 hover:shadow-md transition-shadow cursor-pointer"
            onClick={() => onFightClick(fight.id)}
          >
            <div className="flex justify-between items-center">
              <div>
                <h3 className="font-semibold text-lg">
                  {fight.fighter1_name} vs {fight.fighter2_name}
                </h3>
                <p className="text-gray-600">{fight.weight_class}</p>
                {fight.is_title_fight && (
                  <span className="inline-block bg-yellow-100 text-yellow-800 text-xs px-2 py-1 rounded-full mt-1">
                    Титульный бой
                  </span>
                )}
              </div>
              <div className="text-right">
                <p className="text-sm text-gray-500">{fight.event_name}</p>
                <p className="text-sm text-gray-500">
                  {fight.fight_date ? new Date(fight.fight_date).toLocaleDateString('ru-RU') : 'TBA'}
                </p>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

export default UpcomingFights
