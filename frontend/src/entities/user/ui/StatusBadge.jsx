import styles from './StatusBadge.module.css'

export default function StatusBadge({ blocked }) {
  return (
    <span className={`${styles.badge} ${blocked ? styles.blocked : styles.active}`}>
      <i className={`bi ${blocked ? 'bi-lock-fill' : 'bi-unlock-fill'}`}></i>
      {blocked ? 'Заблокирован' : 'Активен'}
    </span>
  )
}