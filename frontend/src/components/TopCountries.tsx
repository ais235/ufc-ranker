import React from 'react'

interface TopCountriesProps {
  countries: Array<{ country: string; count: number }>
}

const TopCountries: React.FC<TopCountriesProps> = ({ countries }) => {
  if (!countries || countries.length === 0) return null

  return (
    <div className="bg-white rounded-lg shadow-lg p-8">
      <h2 className="text-3xl font-bold text-gray-900 mb-6">
        🌍 Топ страны по количеству бойцов
      </h2>
      <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-5 gap-4">
        {countries.slice(0, 10).map((country, index) => (
          <div key={country.country} className="text-center">
            <div className="text-2xl font-bold text-blue-600">{country.count}</div>
            <div className="text-gray-600">{country.country}</div>
          </div>
        ))}
      </div>
    </div>
  )
}

export default TopCountries
