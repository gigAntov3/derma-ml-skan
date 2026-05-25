import styles from './BlockToggle.module.css'

export default function BlockToggle({ blocked, onChange }) {
  return (
    <div className={styles.wrapper}>
      <div className={styles.row}>
        <div className={styles.info}>
          <i className="bi bi-shield-check"></i>
          <div>
            <span>Блокировка пользователя</span>
            <small>Заблокированный пользователь не может войти в систему</small>
          </div>
        </div>
        <label className={styles.switch}>
          <input 
            type="checkbox" 
            checked={blocked}
            onChange={(e) => onChange(e.target.checked)}
          />
          <span className={styles.slider}></span>
        </label>
      </div>
    </div>
  )
}