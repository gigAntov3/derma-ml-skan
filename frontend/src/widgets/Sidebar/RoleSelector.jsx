import { useState, useMemo, useEffect } from 'react'
import { useNavigate, useLocation } from 'react-router-dom'
import { useAuth } from '../../app/context/AuthContext'
import { ROLES, ROLE_LABELS, ROLE_ICONS } from '../../entities/user/model/role.constants'
import styles from './RoleSelector.module.css'

export default function RoleSelector({ onRoleChange }) {
  const navigate = useNavigate()
  const location = useLocation()
  const { userRoles } = useAuth()
  const [isOpen, setIsOpen] = useState(false)
  const [selectedRole, setSelectedRole] = useState(null)

  const allRoleOptions = [
    { role: ROLES.PATIENT, icon: ROLE_ICONS[ROLES.PATIENT], name: ROLE_LABELS[ROLES.PATIENT], path: '/patient/analysis' },
    { role: ROLES.DOCTOR, icon: ROLE_ICONS[ROLES.DOCTOR], name: ROLE_LABELS[ROLES.DOCTOR], path: '/doctor/patients' },
    { role: ROLES.ADMIN, icon: ROLE_ICONS[ROLES.ADMIN], name: ROLE_LABELS[ROLES.ADMIN], path: '/admin/users' },
    { role: ROLES.DEV, icon: ROLE_ICONS[ROLES.DEV], name: ROLE_LABELS[ROLES.DEV], path: '/dev/models' }
  ]

  const getRoleFromPath = (pathname) => {
    if (pathname.startsWith('/admin')) return ROLES.ADMIN
    if (pathname.startsWith('/doctor')) return ROLES.DOCTOR
    if (pathname.startsWith('/patient')) return ROLES.PATIENT
    if (pathname.startsWith('/dev')) return ROLES.DEV
    return null
  }

  // Инициализация выбранной роли из URL
  useEffect(() => {
    const roleFromPath = getRoleFromPath(location.pathname)
    if (roleFromPath && userRoles?.includes(roleFromPath)) {
      setSelectedRole(roleFromPath)
      if (onRoleChange) {
        onRoleChange(roleFromPath)
      }
    } else if (userRoles && userRoles.length > 0) {
      setSelectedRole(userRoles[0])
      if (onRoleChange) {
        onRoleChange(userRoles[0])
      }
    }
  }, [location.pathname, userRoles])

  const availableRoles = useMemo(() => {
    if (!userRoles || userRoles.length === 0) {
      return [allRoleOptions[0]]
    }
    return allRoleOptions.filter(option => userRoles.includes(option.role))
  }, [userRoles])

  const selectedOption = availableRoles.find(opt => opt.role === selectedRole) || availableRoles[0]

  const toggleDropdown = () => {
    if (availableRoles.length > 1) {
      setIsOpen(!isOpen)
    }
  }
  
  const closeDropdown = () => setIsOpen(false)
  
  const selectRole = (role, path) => {
    setSelectedRole(role)
    closeDropdown()
    if (onRoleChange) {
      onRoleChange(role)
    }
    navigate(path)
  }

  if (availableRoles.length === 0 || !selectedRole) {
    return null
  }

  return (
    <div className={styles.selector}>
      <div className={`${styles.selectedCard} ${isOpen ? styles.expanded : ''}`} onClick={toggleDropdown}>
        <div className={styles.selectedInfo}>
          <i className={`bi ${selectedOption.icon}`}></i>
          <span>{selectedOption.name}</span>
        </div>
        {availableRoles.length > 1 && (
          <i className={`bi bi-chevron-down ${styles.expandIcon}`}></i>
        )}
      </div>
      
      {isOpen && availableRoles.length > 1 && (
        <>
          <div className={styles.dropdown}>
            {availableRoles.map(opt => (
              <div 
                key={opt.role}
                className={`${styles.option} ${selectedRole === opt.role ? styles.active : ''}`}
                onClick={() => selectRole(opt.role, opt.path)}
              >
                <i className={`bi ${opt.icon}`}></i>
                <span className={styles.optionText}>{opt.name}</span>
                {selectedRole === opt.role && <i className="bi bi-check-lg"></i>}
              </div>
            ))}
          </div>
          <div className={styles.overlay} onClick={closeDropdown}></div>
        </>
      )}
    </div>
  )
}