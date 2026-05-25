import AuthLayout from '../../widgets/AuthLayout/AuthLayout'
import LoginForm from '../../features/auth/ui/LoginForm/LoginForm'
import styles from './LoginPage.module.css'

export default function LoginPage() {
  return (
    <div className={styles.page}>
      <AuthLayout>
        <LoginForm />
      </AuthLayout>
    </div>
  )
}