import { ROLE_ICONS, ROLE_LABELS } from '../model/role.constants'
import styles from './RoleBadge.module.css'

export default function RoleBadge({ role }) {
  const icon = ROLE_ICONS[role] || 'bi-person'
  const label = ROLE_LABELS[role] || role
  
  return (
    <span className={`${styles.badge} ${styles[role]}`}>
      <i className={`bi ${icon}`}></i> {label}
    </span>
  )
}