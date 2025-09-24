import React from 'react'
import { Link } from 'react-router-dom'
import { Plus, User } from 'lucide-react'

interface Fighter {
  id: number
  name_ru: string
  name_en?: string
  nickname?: string
  country?: string
  country_flag_url?: string
  image_url?: string
  height?: number
  weight?: number
  reach?: number
  age?: number
}

interface FighterCardProps {
  fighter: Fighter
  rank?: number | string
  isChampion?: boolean
  onAddToCompare?: (fighter: Fighter) => void
  showCompareButton?: boolean
}

const FighterCard: React.FC<FighterCardProps> = ({
  fighter,
  rank,
  isChampion = false,
  onAddToCompare,
  showCompareButton = true
}) => {
  const handleAddToCompare = (e: React.MouseEvent) => {
    e.preventDefault()
    e.stopPropagation()
    onAddToCompare?.(fighter)
  }

  return (
    <div className="card p-4 hover:shadow-lg transition-shadow">
      <Link to={`/fighter/${fighter.id}`} className="block">
        <div className="text-center">
          {/* Ранг */}
          {rank && (
            <div className={`inline-flex items-center justify-center w-8 h-8 rounded-full text-sm font-bold mb-3 ${
              isChampion 
                ? 'bg-ufc-gold text-ufc-dark' 
                : 'bg-ufc-blue text-white'
            }`}>
              {rank}
            </div>
          )}
          
          {/* Фото */}
          <div className="relative mb-4">
            {fighter.image_url ? (
              <img
                src={fighter.image_url}
                alt={fighter.name_ru}
                className="w-32 h-36 object-cover rounded-lg mx-auto border-2 border-gray-200"
                onError={(e) => {
                  e.currentTarget.style.display = 'none'
                  e.currentTarget.nextElementSibling?.classList.remove('hidden')
                }}
              />
            ) : null}
            <div className={`w-32 h-36 bg-gray-200 rounded-lg mx-auto flex items-center justify-center ${fighter.image_url ? 'hidden' : ''}`}>
              <User className="h-12 w-12 text-gray-400" />
            </div>
          </div>
          
          {/* Имя */}
          <h3 className="font-bold text-lg text-gray-900 mb-1">
            {fighter.name_ru}
          </h3>
          
          {fighter.name_en && (
            <p className="text-sm text-gray-600 mb-2">
              {fighter.name_en}
            </p>
          )}
          
          {fighter.nickname && (
            <p className="text-sm text-ufc-gold font-medium mb-2">
              "{fighter.nickname}"
            </p>
          )}
          
          {/* Страна */}
          {fighter.country && (
            <div className="flex items-center justify-center space-x-2 mb-3">
              {fighter.country_flag_url && (
                <img
                  src={fighter.country_flag_url}
                  alt={fighter.country}
                  className="w-4 h-3 object-cover rounded"
                />
              )}
              <span className="text-sm text-gray-600">{fighter.country}</span>
            </div>
          )}
          
          {/* Физические данные */}
          <div className="text-xs text-gray-500 space-y-1">
            {fighter.height && (
              <div>Рост: {fighter.height} см</div>
            )}
            {fighter.weight && (
              <div>Вес: {fighter.weight} кг</div>
            )}
            {fighter.reach && (
              <div>Размах: {fighter.reach} см</div>
            )}
            {fighter.age && (
              <div>Возраст: {fighter.age} лет</div>
            )}
          </div>
        </div>
      </Link>
      
      {/* Кнопка сравнения */}
      {showCompareButton && onAddToCompare && (
        <button
          onClick={handleAddToCompare}
          className="mt-3 w-full btn btn-secondary text-xs"
        >
          <Plus className="h-3 w-3 mr-1" />
          Сравнить
        </button>
      )}
    </div>
  )
}

export default FighterCard




















