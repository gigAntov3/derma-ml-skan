import styles from './FeatureList.module.css'

const features = [
  { icon: 'bi-cpu', text: 'Искусственный интеллект' },
  { icon: 'bi-shield-check', text: 'Безопасность данных' },
  { icon: 'bi-person-badge', text: 'Для врачей и пациентов' }
]

export default function FeatureList() {
  return (
    <div className={styles.features}>
      {features.map((feature, index) => (
        <div key={index} className={styles.item}>
          <i className={`bi ${feature.icon}`}></i>
          <span>{feature.text}</span>
        </div>
      ))}
    </div>
  )
}