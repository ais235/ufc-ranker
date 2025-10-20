import React from 'react'
import { Link, useLocation } from 'react-router-dom'

interface BreadcrumbItem {
  label: string
  path: string
}

const Breadcrumbs: React.FC = () => {
  const location = useLocation()
  
  const generateBreadcrumbs = (): BreadcrumbItem[] => {
    const pathSegments = location.pathname.split('/').filter(segment => segment !== '')
    const breadcrumbs: BreadcrumbItem[] = [
      { label: '🏠 Главная', path: '/' }
    ]

    let currentPath = ''
    
    pathSegments.forEach((segment, index) => {
      currentPath += `/${segment}`
      
      let label = segment
      
      // Преобразуем сегменты в читаемые названия
      switch (segment) {
        case 'rankings':
          label = '🥊 Рейтинги'
          break
        case 'events':
          label = '📅 События'
          break
        case 'fighters':
          label = '👊 Бойцы'
          break
        default:
          // Для конкретных страниц (бойцы, события, рейтинги)
          if (pathSegments[index - 1] === 'fighters') {
            label = segment.replace(/_/g, ' ')
          } else if (pathSegments[index - 1] === 'events') {
            label = segment.replace(/_/g, ' ')
          } else if (pathSegments[index - 1] === 'rankings') {
            // Преобразуем английские названия весовых категорий в русские
            const weightClassMap: { [key: string]: string } = {
              'heavyweight': 'Тяжелый вес',
              'light_heavyweight': 'Полутяжелый вес',
              'middleweight': 'Средний вес',
              'welterweight': 'Полусредний вес',
              'lightweight': 'Легкий вес',
              'featherweight': 'Полулегкий вес',
              'bantamweight': 'Легчайший вес',
              'flyweight': 'Наилегчайший вес',
              "women's_bantamweight": 'Женский легчайший вес',
              "women's_flyweight": 'Женский наилегчайший вес',
              "women's_strawweight": 'Женский минимальный вес'
            }
            label = weightClassMap[segment] || segment.replace(/_/g, ' ')
          }
          break
      }
      
      breadcrumbs.push({ label, path: currentPath })
    })

    return breadcrumbs
  }

  const breadcrumbs = generateBreadcrumbs()

  return (
    <nav className="breadcrumbs mb-6">
      <div className="container mx-auto px-4">
        <div className="flex flex-wrap items-center gap-2 text-sm">
          {breadcrumbs.map((breadcrumb, index) => (
            <React.Fragment key={breadcrumb.path}>
              {index > 0 && <span className="text-gray-400">/</span>}
              {index === breadcrumbs.length - 1 ? (
                <span className="text-yellow-400 font-medium">{breadcrumb.label}</span>
              ) : (
                <Link 
                  to={breadcrumb.path}
                  className="text-gray-300 hover:text-yellow-400 transition-colors"
                >
                  {breadcrumb.label}
                </Link>
              )}
            </React.Fragment>
          ))}
        </div>
      </div>
    </nav>
  )
}

export default Breadcrumbs
