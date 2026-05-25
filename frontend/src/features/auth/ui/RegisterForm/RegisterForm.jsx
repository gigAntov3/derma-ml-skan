import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../../../../app/context/AuthContext'
import Input from '../../../../shared/ui/Input/Input'
import Button from '../../../../shared/ui/Button/Button'
import HintCard from '../../../../shared/ui/HintCard/HintCard'
import { validateRegister } from '../../model/validation'
import styles from './RegisterForm.module.css'

export default function RegisterForm() {
  const navigate = useNavigate()
  const { register, loading } = useAuth()
  const [firstName, setFirstName] = useState('')
  const [lastName, setLastName] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [errors, setErrors] = useState({})
  const [successMessage, setSuccessMessage] = useState('')

  const handleSubmit = async (e) => {
    e.preventDefault()
    
    const validationErrors = validateRegister(firstName, lastName, email, password)
    if (Object.keys(validationErrors).length > 0) {
      setErrors(validationErrors)
      return
    }
    
    setErrors({})
    setSuccessMessage('')
    
    const result = await register({ firstName, lastName, email, password, role: 'patient' })
    
    if (result?.success) {
      setSuccessMessage('Регистрация успешна! Теперь вы можете войти в систему.')
      setTimeout(() => {
        navigate('/login')
      }, 2000)
    }
  }

  return (
    <div className={styles.form}>
      <div className={styles.title}>Регистрация</div>
      <div className={styles.subtitle}>Присоединяйтесь к медицинской платформе</div>
      
      <form onSubmit={handleSubmit}>
        <Input
          label="Имя"
          icon="bi-person"
          placeholder="Введите имя"
          value={firstName}
          onChange={(e) => setFirstName(e.target.value)}
          error={errors.firstName}
        />
        
        <Input
          label="Фамилия"
          icon="bi-person-badge"
          placeholder="Введите фамилию"
          value={lastName}
          onChange={(e) => setLastName(e.target.value)}
          error={errors.lastName}
        />
        
        <Input
          label="Электронная почта"
          icon="bi-envelope"
          type="email"
          placeholder="email@clinic.ru"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          error={errors.email}
        />
        
        <Input
          label="Пароль"
          icon="bi-lock"
          type="password"
          placeholder="Минимум 6 символов"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          error={errors.password}
        />
        
        {successMessage && (
          <div className={styles.successMessage}>{successMessage}</div>
        )}
        
        <Button type="submit" icon="bi-person-plus" loading={loading}>
          Создать аккаунт
        </Button>
      </form>
      
      <div className={styles.footer}>
        <Link to="/login" className={styles.link}>
          Уже есть аккаунт? <span>Войти</span>
        </Link>
      </div>
    </div>
  )
}