import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../../../../app/context/AuthContext'
import Input from '../../../../shared/ui/Input/Input'
import Button from '../../../../shared/ui/Button/Button'
import HintCard from '../../../../shared/ui/HintCard/HintCard'
import { validateLogin } from '../../model/validation'
import styles from './LoginForm.module.css'

export default function LoginForm() {
  const navigate = useNavigate()
  const { login, loading, error } = useAuth()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [errors, setErrors] = useState({})
  const [serverError, setServerError] = useState('')

  // Функция для определения пути редиректа в зависимости от роли
  const getRedirectPath = (user) => {
    // Проверяем роли пользователя
    if (user?.roles?.includes('admin')) {
      return '/admin/users'
    }
    if (user?.roles?.includes('dev')) {
        return '/dev/models'
    }
    if (user?.roles?.includes('doctor')) {
      return '/doctor/patients'
    }
    if (user?.roles?.includes('patient')) {
      return '/patient/doctors'
    }
    return '/patient/doctors'
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    
    const validationErrors = validateLogin(email, password)
    if (Object.keys(validationErrors).length > 0) {
      setErrors(validationErrors)
      return
    }
    
    setErrors({})
    setServerError('')
    
    const result = await login(email, password)
    
    if (result?.success) {
      // Получаем пользователя из localStorage после успешного входа
      const storedUser = localStorage.getItem('dermaclinic_user')
      if (storedUser) {
        const user = JSON.parse(storedUser)
        const redirectPath = getRedirectPath(user)
        navigate(redirectPath)
      } else {
        // Fallback - если что-то пошло не так
        navigate('/patient/doctors')
      }
    } else if (error) {
      setServerError(error)
    }
  }

  return (
    <div className={styles.form}>
      <div className={styles.title}>Добро пожаловать</div>
      <div className={styles.subtitle}>Войдите в свою учетную запись</div>
      
      <form onSubmit={handleSubmit}>
        <Input
          label="Электронная почта"
          icon="bi-envelope"
          type="email"
          placeholder="patient@dermaclinic.ru"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          error={errors.email}
        />
        
        <Input
          label="Пароль"
          icon="bi-lock"
          type="password"
          placeholder="••••••••"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          error={errors.password}
        />
        
        {(serverError || error) && (
          <div className={styles.errorMessage}>{serverError || error}</div>
        )}
        
        <Button type="submit" icon="bi-box-arrow-in-right" loading={loading}>
          Войти в систему
        </Button>
      </form>
      
      <div className={styles.footer}>
        <Link to="/register" className={styles.link}>
          Нет аккаунта? <span>Создать учетную запись</span>
        </Link>
      </div>
    </div>
  )
}