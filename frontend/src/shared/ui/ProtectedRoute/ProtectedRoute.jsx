import { Navigate } from 'react-router-dom'
import { useAuth } from '../../../app/context/AuthContext'

export default function ProtectedRoute({ children }) {
  const { isAuthenticated, loading, user } = useAuth()

  console.log('ProtectedRoute debug:', {
    isAuthenticated,
    loading,
    user,
    userRoles: user?.roles,
    pathname: window.location.pathname
  })

  if (loading) {
    return <div>Загрузка...</div>
  }

  if (!isAuthenticated) {
    console.log('Redirecting to login: not authenticated')
    return <Navigate to="/login" replace />
  }

  // Проверяем, есть ли у пользователя доступ к запрашиваемому пути
  const pathname = window.location.pathname
  
  if (pathname.startsWith('/patient') && !user?.roles?.includes('patient')) {
    console.log('Redirecting to login: patient access denied')
    return <Navigate to="/login" replace />
  }
  
  if (pathname.startsWith('/doctor') && !user?.roles?.includes('doctor')) {
    console.log('Redirecting to login: doctor access denied', { 
      roles: user?.roles, 
      includesDoctor: user?.roles?.includes('doctor') 
    })
    return <Navigate to="/login" replace />
  }
  
  if (pathname.startsWith('/admin') && !user?.roles?.includes('admin')) {
    console.log('Redirecting to login: admin access denied')
    return <Navigate to="/login" replace />
  }
  
  if (pathname.startsWith('/dev') && !user?.roles?.includes('dev')) {
    console.log('Redirecting to login: dev access denied')
    return <Navigate to="/login" replace />
  }

  console.log('Access granted')
  return children
}