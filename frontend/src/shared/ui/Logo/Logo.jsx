import styles from './Logo.module.css'

export default function Logo() {
  return (
    <div className={styles.logo}>
      <div className={styles.icon}>
        <i className="bi bi-exclude"></i>
      </div>
      <h1 className={styles.title}>DermaSkan</h1>
      <p className={styles.subtitle}>AI-платформа для диагностики и лечения заболеваний кожи</p>
    </div>
  )
}