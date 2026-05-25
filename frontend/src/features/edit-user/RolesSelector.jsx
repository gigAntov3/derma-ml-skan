import { ROLES, ROLE_LABELS, ROLE_ICONS } from '../../entities/user/model/role.constants'
import styles from './RolesSelector.module.css'

export default function RolesSelector({ selectedRoles, onChange }) {
  const roles = [
    { role: ROLES.PATIENT, icon: ROLE_ICONS[ROLES.PATIENT], label: ROLE_LABELS[ROLES.PATIENT] },
    { role: ROLES.DOCTOR, icon: ROLE_ICONS[ROLES.DOCTOR], label: ROLE_LABELS[ROLES.DOCTOR] },
    { role: ROLES.ADMIN, icon: ROLE_ICONS[ROLES.ADMIN], label: ROLE_LABELS[ROLES.ADMIN] },
    { role: ROLES.DEV, icon: ROLE_ICONS[ROLES.DEV], label: ROLE_LABELS[ROLES.DEV] }
  ]

  const toggleRole = (role) => {
    if (selectedRoles.includes(role)) {
      onChange(selectedRoles.filter(r => r !== role))
    } else {
      onChange([...selectedRoles, role])
    }
  }

  return (
    <div className={styles.grid}>
      {roles.map(({ role, icon, label }) => (
        <div 
          key={role}
          className={`${styles.card} ${selectedRoles.includes(role) ? styles.active : ''}`}
          onClick={() => toggleRole(role)}
        >
          <i className={`bi ${icon} ${styles.icon}`}></i>
          <span className={styles.label}>{label}</span>
        </div>
      ))}
    </div>
  )
}