import React from 'react'
import { Link, useLocation } from 'react-router-dom'
import { Trophy, Users, Scale, Calendar } from 'lucide-react'

const Header: React.FC = () => {
  const location = useLocation()

  const navItems = [
    { path: '/', label: 'Рейтинги', icon: Trophy },
    { path: '/compare', label: 'Сравнение', icon: Scale },
    { path: '/upcoming', label: 'Карды', icon: Calendar },
  ]

  return (
    <header className="bg-ufc-dark text-white shadow-lg">
      <div className="container mx-auto px-4">
        <div className="flex items-center justify-between h-16">
          <Link to="/" className="flex items-center space-x-2">
            <Trophy className="h-8 w-8 text-ufc-gold" />
            <span className="text-xl font-bold">UFC Ranker</span>
          </Link>
          
          <nav className="flex space-x-8">
            {navItems.map(({ path, label, icon: Icon }) => (
              <Link
                key={path}
                to={path}
                className={`flex items-center space-x-2 px-3 py-2 rounded-md transition-colors ${
                  location.pathname === path
                    ? 'bg-ufc-gold text-ufc-dark'
                    : 'text-gray-300 hover:text-white hover:bg-gray-700'
                }`}
              >
                <Icon className="h-4 w-4" />
                <span>{label}</span>
              </Link>
            ))}
          </nav>
        </div>
      </div>
    </header>
  )
}

export default Header




















