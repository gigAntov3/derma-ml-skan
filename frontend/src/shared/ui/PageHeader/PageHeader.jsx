import styles from './PageHeader.module.css'

export default function PageHeader({ title, icon, description, actions }) {
  return (
    <div className={styles.header}>
      <div className={styles.titleSection}>
        <h2>
          {icon && <i className={`bi ${icon}`}></i>}
          {title}
        </h2>
        {description && (
          <small>
            {description}
          </small>
        )}
      </div>
      {actions && (
        <div className={styles.actions}>
          {actions}
        </div>
      )}
    </div>
  )
}