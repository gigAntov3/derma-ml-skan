import { useState, useEffect } from 'react'
import { useLocation } from 'react-router-dom'
import { useAuth } from '../../app/context/AuthContext'
import RoleSelector from './RoleSelector'
import Navigation from './Navigation'
import ProfileModal from '../../features/profile/ui/ProfileModal/ProfileModal'
import { useToast } from '../../shared/hooks/useToast'
import styles from './Sidebar.module.css'

export default function Sidebar({ onLogout }) {
  const [isProfileModalOpen, setIsProfileModalOpen] = useState(false)
  const [currentRole, setCurrentRole] = useState(null)
  const location = useLocation()
  const { showToast } = useToast()
  const { user, updateUserProfile } = useAuth() // Получаем пользователя из контекста

  // Функция для определения роли по URL
  const getRoleFromPath = (pathname) => {
    if (pathname.startsWith('/admin')) return 'admin'
    if (pathname.startsWith('/doctor')) return 'doctor'
    if (pathname.startsWith('/patient')) return 'patient'
    if (pathname.startsWith('/dev')) return 'dev'
    return null
  }

  // При загрузке и при изменении URL обновляем роль
  useEffect(() => {
    const roleFromPath = getRoleFromPath(location.pathname)
    if (roleFromPath) {
      setCurrentRole(roleFromPath)
      localStorage.setItem('selected_role', roleFromPath)
    } else {
      const savedRole = localStorage.getItem('selected_role')
      if (savedRole) {
        setCurrentRole(savedRole)
      }
    }
  }, [location.pathname])

  const handleSaveProfile = () => {
    // Не нужно передавать данные, так как ProfileModal сам вызовет updateUserProfile
    showToast('Личная информация сохранена', '#1f7a63')
  }

  const handleRoleChange = (role) => {
    setCurrentRole(role)
    localStorage.setItem('selected_role', role)
  }

  // Преобразуем данные пользователя для ProfileModal
  const userForModal = user ? {
    firstName: user.firstName || user.first_name,
    lastName: user.lastName || user.last_name,
    middleName: user.middleName || user.middle_name,
    phone: user.phone,
    email: user.email,
    birthDate: user.birthDate || user.birth_date,
  } : null

  return (
    <>
      <div className={styles.sidebar}>
        <div className={styles.logo}>
          <i className="bi bi-exclude"></i>
          <span>DermaSkan</span>
        </div>
        
        <RoleSelector onRoleChange={handleRoleChange} />
        
        <Navigation currentRole={currentRole} />
        
        <div className={styles.profileExitRow}>
          <button 
            className={styles.profileNavBtn}
            onClick={() => setIsProfileModalOpen(true)}
          >
            <i className="bi bi-person-circle"></i>
            <span>Мой профиль</span>
          </button>
          <button 
            className={styles.exitIconBtn}
            onClick={onLogout}
            title="Выйти"
          >
            <i className="bi bi-box-arrow-right"></i>
          </button>
        </div>
      </div>

      <ProfileModal 
        isOpen={isProfileModalOpen}
        onClose={() => setIsProfileModalOpen(false)}
        onSave={handleSaveProfile}
        userData={userForModal}
      />
    </>
  )
}