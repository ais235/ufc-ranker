import React from 'react'
import { Trophy, Users } from 'lucide-react'

interface WeightClass {
  id: number
  name_ru: string
  name_en?: string
  gender: string
  is_p4p: boolean
}

interface WeightClassTabsProps {
  weightClasses: WeightClass[]
  activeClassId: number | null
  onClassChange: (classId: number) => void
}

const WeightClassTabs: React.FC<WeightClassTabsProps> = ({
  weightClasses,
  activeClassId,
  onClassChange
}) => {
  // Разделяем категории на мужские, женские и P4P
  const maleClasses = weightClasses.filter(wc => wc.gender === 'male' && !wc.is_p4p)
  const femaleClasses = weightClasses.filter(wc => wc.gender === 'female' && !wc.is_p4p)
  const p4pClasses = weightClasses.filter(wc => wc.is_p4p)

  const renderTab = (weightClass: WeightClass) => (
    <button
      key={weightClass.id}
      onClick={() => onClassChange(weightClass.id)}
      className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
        activeClassId === weightClass.id
          ? 'bg-ufc-blue text-white'
          : 'bg-white text-gray-700 hover:bg-gray-100'
      }`}
    >
      {weightClass.name_ru}
    </button>
  )

  return (
    <div className="space-y-6">
      {/* P4P категории */}
      {p4pClasses.length > 0 && (
        <div>
          <div className="flex items-center space-x-2 mb-3">
            <Trophy className="h-5 w-5 text-ufc-gold" />
            <h3 className="text-lg font-semibold text-gray-900">Pound for Pound</h3>
          </div>
          <div className="flex flex-wrap gap-2">
            {p4pClasses.map(renderTab)}
          </div>
        </div>
      )}

      {/* Мужские категории */}
      {maleClasses.length > 0 && (
        <div>
          <div className="flex items-center space-x-2 mb-3">
            <Users className="h-5 w-5 text-ufc-blue" />
            <h3 className="text-lg font-semibold text-gray-900">Мужские категории</h3>
          </div>
          <div className="flex flex-wrap gap-2">
            {maleClasses.map(renderTab)}
          </div>
        </div>
      )}

      {/* Женские категории */}
      {femaleClasses.length > 0 && (
        <div>
          <div className="flex items-center space-x-2 mb-3">
            <Users className="h-5 w-5 text-pink-500" />
            <h3 className="text-lg font-semibold text-gray-900">Женские категории</h3>
          </div>
          <div className="flex flex-wrap gap-2">
            {femaleClasses.map(renderTab)}
          </div>
        </div>
      )}
    </div>
  )
}

export default WeightClassTabs













