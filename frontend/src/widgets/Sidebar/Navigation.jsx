import { useNavigate, useLocation } from 'react-router-dom'
import styles from './Navigation.module.css'

export default function Navigation({ currentRole }) {
  const navigate = useNavigate()
  const location = useLocation()

  // Определяем активную роль (если не передана, пробуем определить из URL)
  const getRoleFromPath = (pathname) => {
    if (pathname.startsWith('/admin')) return 'admin'
    if (pathname.startsWith('/doctor')) return 'doctor'
    if (pathname.startsWith('/patient')) return 'patient'
    if (pathname.startsWith('/dev')) return 'dev'
    return currentRole || 'patient'
  }

  const activeRole = currentRole || getRoleFromPath(location.pathname)

  // Навигация для администратора
  const adminNavItems = [
    { icon: 'bi-people', label: 'Пользователи', path: '/admin/users' },
  ]

  // Навигация для врача
  const doctorNavItems = [
    { icon: 'bi-people', label: 'Мои пациенты', path: '/doctor/patients' },
  ]

  // Навигация для пациента
  const patientNavItems = [
    { icon: 'bi-camera', label: 'Анализ кожи', path: '/patient/analysis' },
    { icon: 'bi-heart-pulse', label: 'Мои врачи', path: '/patient/doctors' },
    { icon: 'bi-file-medical', label: 'Диагноз', path: '/patient/diagnosis' },
    { icon: 'bi-clock-history', label: 'История анализов', path: '/patient/history' },
  ]

  // Навигация для разработчика
  const devNavItems = [
    { icon: 'bi-cpu', label: 'ML модели', path: '/dev/models' },
  ]

  // Получаем навигацию в зависимости от роли
  const getNavItems = () => {
    switch (activeRole) {
      case 'admin':
        return adminNavItems
      case 'doctor':
        return doctorNavItems
      case 'patient':
        return patientNavItems
      case 'dev':
        return devNavItems
      default:
        return patientNavItems
    }
  }

  const navItems = getNavItems()
  const hasMainSection = navItems.length > 0

  const handleNavigation = (path) => {
    navigate(path)
  }

  const isActive = (path) => {
    return location.pathname === path
  }

  return (
    <div className={styles.navContainer}>
      {hasMainSection && (
        <div className={styles.navSection}>
          {navItems.map((item, idx) => (
            <a 
              key={idx} 
              className={`${styles.navLink} ${isActive(item.path) ? styles.active : ''}`}
              onClick={() => handleNavigation(item.path)}
            >
              <i className={`bi ${item.icon}`}></i> {item.label}
            </a>
          ))}
        </div>
      )}
    </div>
  )
}