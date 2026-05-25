import styles from './HintCard.module.css'

export default function HintCard({ icon, children }) {
  return (
    <div className={styles.hint}>
      <i className={`bi ${icon}`}></i>
      <span>{children}</span>
    </div>
  )
}