import React from 'react'
import { Link, useLocation } from 'react-router-dom'

const SiteHeader: React.FC = () => {
  const location = useLocation()

  const isActive = (path: string) => {
    return location.pathname === path
  }

  return (
    <header className="site-header">
      <div className="container mx-auto px-4">
        <div className="flex flex-col md:flex-row items-center justify-between">
          <Link to="/" className="text-2xl md:text-3xl font-bold text-black mb-4 md:mb-0">
            🥊 UFC Ranker
          </Link>
          
          <nav className="flex flex-wrap justify-center gap-2 md:gap-4">
            <Link
              to="/"
              className={`px-4 py-2 rounded-lg transition-colors ${
                isActive('/') 
                  ? 'bg-black text-yellow-400' 
                  : 'text-black hover:bg-black hover:text-yellow-400'
              }`}
            >
              🏠 Главная
            </Link>
            <Link
              to="/rankings"
              className={`px-4 py-2 rounded-lg transition-colors ${
                isActive('/rankings') || location.pathname.startsWith('/rankings/')
                  ? 'bg-black text-yellow-400' 
                  : 'text-black hover:bg-black hover:text-yellow-400'
              }`}
            >
              🥊 Рейтинги
            </Link>
            <Link
              to="/events"
              className={`px-4 py-2 rounded-lg transition-colors ${
                isActive('/events') || location.pathname.startsWith('/events/')
                  ? 'bg-black text-yellow-400' 
                  : 'text-black hover:bg-black hover:text-yellow-400'
              }`}
            >
              📅 События
            </Link>
            <Link
              to="/fighters"
              className={`px-4 py-2 rounded-lg transition-colors ${
                isActive('/fighters') || location.pathname.startsWith('/fighters/')
                  ? 'bg-black text-yellow-400' 
                  : 'text-black hover:bg-black hover:text-yellow-400'
              }`}
            >
              👊 Бойцы
            </Link>
          </nav>
        </div>
      </div>
    </header>
  )
}

export default SiteHeader
