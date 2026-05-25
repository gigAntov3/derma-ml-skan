import AuthLayout from '../../widgets/AuthLayout/AuthLayout'
import RegisterForm from '../../features/auth/ui/RegisterForm/RegisterForm'
import styles from './RegisterPage.module.css'

export default function RegisterPage() {
  return (
    <div className={styles.page}>
      <AuthLayout>
        <RegisterForm />
      </AuthLayout>
    </div>
  )
}