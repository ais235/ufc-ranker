import React from 'react'
import { Fight } from '../types'

interface FightCardProps {
  fight: Fight
  onFighterClick?: (fighterName: string) => void
}

const FightCard: React.FC<FightCardProps> = ({ fight, onFighterClick }) => {
  const getResultColor = () => {
    if (fight.is_win === '1') return 'text-green-400'
    if (fight.is_loss === '1') return 'text-red-400'
    if (fight.is_draw === '1') return 'text-yellow-400'
    if (fight.is_nc === '1') return 'text-gray-400'
    return 'text-white'
  }

  const getResultText = () => {
    if (fight.is_win === '1') return 'Победа'
    if (fight.is_loss === '1') return 'Поражение'
    if (fight.is_draw === '1') return 'Ничья'
    if (fight.is_nc === '1') return 'Не состоялся'
    return 'Результат неизвестен'
  }

  return (
    <div className="bg-white bg-opacity-10 backdrop-blur-lg border border-white border-opacity-20 rounded-xl p-6 hover:bg-opacity-20 transition-all duration-300">
      <div className="flex justify-between items-start mb-4">
        <div className="flex-1">
          <div className="flex items-center gap-4 mb-2">
            <h3 className="text-lg font-semibold text-white">
              {fight.fighter1_name}
            </h3>
            <span className="text-gray-300">vs</span>
            <h3 className="text-lg font-semibold text-white">
              {fight.fighter2_name}
            </h3>
          </div>
          <p className="text-yellow-400 font-medium">{fight.weight_class}</p>
        </div>
        
        {fight.is_title_fight && (
          <span className="bg-yellow-500 text-black px-3 py-1 rounded-full text-xs font-bold">
            Титульный бой
          </span>
        )}
      </div>

      <div className="grid grid-cols-2 gap-4 text-sm">
        <div>
          <p className="text-gray-300">Способ:</p>
          <p className="text-white font-medium">{fight.method || 'Не указан'}</p>
        </div>
        <div>
          <p className="text-gray-300">Раунд:</p>
          <p className="text-white font-medium">{fight.round || 'Не указан'}</p>
        </div>
        <div>
          <p className="text-gray-300">Время:</p>
          <p className="text-white font-medium">{fight.time || 'Не указано'}</p>
        </div>
        <div>
          <p className="text-gray-300">Результат:</p>
          <p className={`font-medium ${getResultColor()}`}>
            {getResultText()}
          </p>
        </div>
      </div>

      {fight.method_details && (
        <div className="mt-4 p-3 bg-gray-800 bg-opacity-50 rounded-lg">
          <p className="text-gray-300 text-sm">{fight.method_details}</p>
        </div>
      )}

      <div className="mt-4 flex justify-between text-xs text-gray-400">
        <span>{fight.fighter1_record}</span>
        <span>{fight.fighter2_record}</span>
      </div>
    </div>
  )
}

export default FightCard
