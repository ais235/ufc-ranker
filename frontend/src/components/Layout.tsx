import React from 'react'
import SiteHeader from './SiteHeader'
import Breadcrumbs from './Breadcrumbs'

interface LayoutProps {
  children: React.ReactNode
}

const Layout: React.FC<LayoutProps> = ({ children }) => {
  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 to-gray-800 text-white">
      <div className="container mx-auto px-4 py-6">
        <SiteHeader />
        <Breadcrumbs />
        <main>
          {children}
        </main>
      </div>
    </div>
  )
}

export default Layout
