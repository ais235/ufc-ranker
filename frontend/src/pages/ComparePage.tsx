import React, { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { ArrowLeft, User, Trophy, Ruler, Weight, Target, Calendar } from 'lucide-react'
import { api } from '../services/api'
import { FighterDetail, Comparison } from '../types'

const ComparePage: React.FC = () => {
  const [fighter1Id, setFighter1Id] = useState<number | null>(null)
  const [fighter2Id, setFighter2Id] = useState<number | null>(null)
  const [comparison, setComparison] = useState<Comparison | null>(null)
  const [loading, setLoading] = useState(false)
  const [fighters, setFighters] = useState<FighterDetail[]>([])

  useEffect(() => {
    loadFighters()
  }, [])

  const loadFighters = async () => {
    try {
      const fightersData = await api.getFighters({ limit: 100 })
      setFighters(fightersData)
    } catch (error) {
      console.error('Ошибка загрузки бойцов:', error)
    }
  }

  const handleCompare = async () => {
    if (!fighter1Id || !fighter2Id) {
      alert('Выберите двух бойцов для сравнения')
      return
    }

    if (fighter1Id === fighter2Id) {
      alert('Выберите разных бойцов')
      return
    }

    try {
      setLoading(true)
      const comparisonData = await api.compareFighters(fighter1Id, fighter2Id)
      setComparison(comparisonData)
    } catch (error) {
      console.error('Ошибка сравнения:', error)
      alert('Ошибка при сравнении бойцов')
    } finally {
      setLoading(false)
    }
  }

  const getAdvantage = (value1: number | null, value2: number | null) => {
    if (!value1 || !value2) return 'neutral'
    if (value1 > value2) return 'fighter1'
    if (value2 > value1) return 'fighter2'
    return 'neutral'
  }

  const getAdvantageClass = (advantage: string, isFighter1: boolean) => {
    if (advantage === 'neutral') return 'bg-gray-100'
    if (advantage === 'fighter1' && isFighter1) return 'bg-green-100'
    if (advantage === 'fighter2' && !isFighter1) return 'bg-green-100'
    return 'bg-gray-100'
  }

  return (
    <div className="max-w-6xl mx-auto">
      {/* Навигация */}
      <div className="mb-6">
        <Link to="/" className="btn btn-secondary">
          <ArrowLeft className="h-4 w-4 mr-2" />
          Назад к рейтингам
        </Link>
      </div>

      <div className="card p-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-8 text-center">
          Сравнение бойцов
        </h1>

        {/* Выбор бойцов */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Боец 1
            </label>
            <select
              value={fighter1Id || ''}
              onChange={(e) => setFighter1Id(parseInt(e.target.value) || null)}
              className="input w-full"
            >
              <option value="">Выберите бойца</option>
              {fighters.map(fighter => (
                <option key={fighter.id} value={fighter.id}>
                  {fighter.name_ru} {fighter.nickname ? `"${fighter.nickname}"` : ''}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Боец 2
            </label>
            <select
              value={fighter2Id || ''}
              onChange={(e) => setFighter2Id(parseInt(e.target.value) || null)}
              className="input w-full"
            >
              <option value="">Выберите бойца</option>
              {fighters.map(fighter => (
                <option key={fighter.id} value={fighter.id}>
                  {fighter.name_ru} {fighter.nickname ? `"${fighter.nickname}"` : ''}
                </option>
              ))}
            </select>
          </div>
        </div>

        <div className="text-center mb-8">
          <button
            onClick={handleCompare}
            disabled={loading || !fighter1Id || !fighter2Id}
            className="btn btn-primary px-8 py-3"
          >
            {loading ? 'Сравниваем...' : 'Сравнить бойцов'}
          </button>
        </div>

        {/* Результаты сравнения */}
        {comparison && (
          <div className="space-y-8">
            {/* Заголовки бойцов */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="text-center">
                <div className="relative mb-4">
                  {comparison.fighter1.image_url ? (
                    <img
                      src={comparison.fighter1.image_url}
                      alt={comparison.fighter1.name_ru}
                      className="w-32 h-40 object-cover rounded-lg mx-auto border-2 border-gray-200"
                    />
                  ) : (
                    <div className="w-32 h-40 bg-gray-200 rounded-lg mx-auto flex items-center justify-center">
                      <User className="h-12 w-12 text-gray-400" />
                    </div>
                  )}
                </div>
                <h3 className="text-xl font-bold text-gray-900">
                  {comparison.fighter1.name_ru}
                </h3>
                {comparison.fighter1.nickname && (
                  <p className="text-ufc-gold font-medium">
                    "{comparison.fighter1.nickname}"
                  </p>
                )}
                {comparison.fighter1.country && (
                  <p className="text-gray-600">{comparison.fighter1.country}</p>
                )}
              </div>

              <div className="text-center">
                <div className="relative mb-4">
                  {comparison.fighter2.image_url ? (
                    <img
                      src={comparison.fighter2.image_url}
                      alt={comparison.fighter2.name_ru}
                      className="w-32 h-40 object-cover rounded-lg mx-auto border-2 border-gray-200"
                    />
                  ) : (
                    <div className="w-32 h-40 bg-gray-200 rounded-lg mx-auto flex items-center justify-center">
                      <User className="h-12 w-12 text-gray-400" />
                    </div>
                  )}
                </div>
                <h3 className="text-xl font-bold text-gray-900">
                  {comparison.fighter2.name_ru}
                </h3>
                {comparison.fighter2.nickname && (
                  <p className="text-ufc-gold font-medium">
                    "{comparison.fighter2.nickname}"
                  </p>
                )}
                {comparison.fighter2.country && (
                  <p className="text-gray-600">{comparison.fighter2.country}</p>
                )}
              </div>
            </div>

            {/* Таблица сравнения */}
            <div className="overflow-x-auto">
              <table className="w-full border-collapse">
                <thead>
                  <tr className="bg-gray-50">
                    <th className="border border-gray-300 px-4 py-2 text-left">Параметр</th>
                    <th className="border border-gray-300 px-4 py-2 text-center">
                      {comparison.fighter1.name_ru}
                    </th>
                    <th className="border border-gray-300 px-4 py-2 text-center">
                      {comparison.fighter2.name_ru}
                    </th>
                  </tr>
                </thead>
                <tbody>
                  {/* Рост */}
                  <tr>
                    <td className="border border-gray-300 px-4 py-2 font-medium">
                      <div className="flex items-center space-x-2">
                        <Ruler className="h-4 w-4 text-ufc-blue" />
                        <span>Рост</span>
                      </div>
                    </td>
                    <td className={`border border-gray-300 px-4 py-2 text-center ${getAdvantageClass(getAdvantage(comparison.comparison.height.fighter1, comparison.comparison.height.fighter2), true)}`}>
                      {comparison.comparison.height.fighter1 ? `${comparison.comparison.height.fighter1} см` : '—'}
                    </td>
                    <td className={`border border-gray-300 px-4 py-2 text-center ${getAdvantageClass(getAdvantage(comparison.comparison.height.fighter1, comparison.comparison.height.fighter2), false)}`}>
                      {comparison.comparison.height.fighter2 ? `${comparison.comparison.height.fighter2} см` : '—'}
                    </td>
                  </tr>

                  {/* Вес */}
                  <tr>
                    <td className="border border-gray-300 px-4 py-2 font-medium">
                      <div className="flex items-center space-x-2">
                        <Weight className="h-4 w-4 text-ufc-blue" />
                        <span>Вес</span>
                      </div>
                    </td>
                    <td className={`border border-gray-300 px-4 py-2 text-center ${getAdvantageClass(getAdvantage(comparison.comparison.weight.fighter1, comparison.comparison.weight.fighter2), true)}`}>
                      {comparison.comparison.weight.fighter1 ? `${comparison.comparison.weight.fighter1} кг` : '—'}
                    </td>
                    <td className={`border border-gray-300 px-4 py-2 text-center ${getAdvantageClass(getAdvantage(comparison.comparison.weight.fighter1, comparison.comparison.weight.fighter2), false)}`}>
                      {comparison.comparison.weight.fighter2 ? `${comparison.comparison.weight.fighter2} кг` : '—'}
                    </td>
                  </tr>

                  {/* Размах рук */}
                  <tr>
                    <td className="border border-gray-300 px-4 py-2 font-medium">
                      <div className="flex items-center space-x-2">
                        <Target className="h-4 w-4 text-ufc-blue" />
                        <span>Размах рук</span>
                      </div>
                    </td>
                    <td className={`border border-gray-300 px-4 py-2 text-center ${getAdvantageClass(getAdvantage(comparison.comparison.reach.fighter1, comparison.comparison.reach.fighter2), true)}`}>
                      {comparison.comparison.reach.fighter1 ? `${comparison.comparison.reach.fighter1} см` : '—'}
                    </td>
                    <td className={`border border-gray-300 px-4 py-2 text-center ${getAdvantageClass(getAdvantage(comparison.comparison.reach.fighter1, comparison.comparison.reach.fighter2), false)}`}>
                      {comparison.comparison.reach.fighter2 ? `${comparison.comparison.reach.fighter2} см` : '—'}
                    </td>
                  </tr>

                  {/* Возраст */}
                  <tr>
                    <td className="border border-gray-300 px-4 py-2 font-medium">
                      <div className="flex items-center space-x-2">
                        <Calendar className="h-4 w-4 text-ufc-blue" />
                        <span>Возраст</span>
                      </div>
                    </td>
                    <td className={`border border-gray-300 px-4 py-2 text-center ${getAdvantageClass(getAdvantage(comparison.comparison.age.fighter1, comparison.comparison.age.fighter2), true)}`}>
                      {comparison.comparison.age.fighter1 ? `${comparison.comparison.age.fighter1} лет` : '—'}
                    </td>
                    <td className={`border border-gray-300 px-4 py-2 text-center ${getAdvantageClass(getAdvantage(comparison.comparison.age.fighter1, comparison.comparison.age.fighter2), false)}`}>
                      {comparison.comparison.age.fighter2 ? `${comparison.comparison.age.fighter2} лет` : '—'}
                    </td>
                  </tr>

                  {/* Боевой рекорд */}
                  {comparison.fighter1.fight_record && comparison.fighter2.fight_record && (
                    <tr>
                      <td className="border border-gray-300 px-4 py-2 font-medium">
                        <div className="flex items-center space-x-2">
                          <Trophy className="h-4 w-4 text-ufc-gold" />
                          <span>Рекорд</span>
                        </div>
                      </td>
                      <td className="border border-gray-300 px-4 py-2 text-center">
                        {comparison.fighter1.fight_record.wins}-{comparison.fighter1.fight_record.losses}-{comparison.fighter1.fight_record.draws}
                        <br />
                        <span className="text-sm text-gray-600">
                          {comparison.fighter1.fight_record.win_percentage}% побед
                        </span>
                      </td>
                      <td className="border border-gray-300 px-4 py-2 text-center">
                        {comparison.fighter2.fight_record.wins}-{comparison.fighter2.fight_record.losses}-{comparison.fighter2.fight_record.draws}
                        <br />
                        <span className="text-sm text-gray-600">
                          {comparison.fighter2.fight_record.win_percentage}% побед
                        </span>
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default ComparePage
