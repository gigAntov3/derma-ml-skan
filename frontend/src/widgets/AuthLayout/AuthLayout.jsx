import Logo from '../../shared/ui/Logo/Logo'
import FeatureList from '../../shared/ui/FeatureList/FeatureList'
import styles from './AuthLayout.module.css'

export default function AuthLayout({ children }) {
  return (
    <div className={styles.container}>
      <div className={styles.brand}>
        <Logo />
        <FeatureList />
        <div className={styles.footer}>
          <i className="bi bi-droplet-half"></i> Современная дерматология
        </div>
      </div>
      <div className={styles.form}>
        {children}
      </div>
    </div>
  )
}