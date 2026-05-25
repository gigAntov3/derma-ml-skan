import { ROLES, ROLE_LABELS } from '../../entities/user/model/role.constants'
import styles from './RoleFilter.module.css'

export default function RoleFilter({ value, onChange }) {
  return (
    <div className={styles.wrapper}>
      <i className="bi bi-funnel"></i>
      <select 
        className={styles.select}
        value={value}
        onChange={(e) => onChange(e.target.value)}
      >
        <option value="all">Все роли</option>
        <option value={ROLES.PATIENT}>{ROLE_LABELS[ROLES.PATIENT]}</option>
        <option value={ROLES.DOCTOR}>{ROLE_LABELS[ROLES.DOCTOR]}</option>
        <option value={ROLES.ADMIN}>{ROLE_LABELS[ROLES.ADMIN]}</option>
        <option value={ROLES.DEV}>{ROLE_LABELS[ROLES.DEV]}</option>
      </select>
    </div>
  )
}