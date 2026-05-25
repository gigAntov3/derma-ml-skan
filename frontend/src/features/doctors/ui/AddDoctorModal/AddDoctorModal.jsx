import { useState } from 'react'
import Modal from '../../../../shared/ui/Modal/Modal'
import Button from '../../../../shared/ui/Button/Button'
import Input from '../../../../shared/ui/Input/Input'
import styles from './AddDoctorModal.module.css'

export default function AddDoctorModal({ isOpen, onClose, onAdd }) {
  const [email, setEmail] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const handleSubmit = async () => {
    if (!email.trim()) {
      setError('Введите email врача')
      return
    }

    setLoading(true)
    setError('')
    
    try {
      await onAdd(email)
      setEmail('')
      onClose()
    } catch (err) {
      setError(err.message || 'Ошибка добавления')
    } finally {
      setLoading(false)
    }
  }

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="Добавление врача">
      <div className={styles.content}>
        <p className={styles.description}>
          <i className="bi bi-info-circle"></i>
          Введите email врача, чтобы добавить его в свой список
        </p>
        
        <Input
          label="Email врача"
          icon="bi-envelope"
          type="email"
          placeholder="doctor@dermaclinic.ru"
          value={email}
          onChange={(e) => {
            setEmail(e.target.value)
            setError('')
          }}
          error={error}
        />
        
        <div className={styles.actions}>
          <Button variant="secondary" onClick={onClose}>
            Отмена
          </Button>
          <Button onClick={handleSubmit} loading={loading}>
            <i className="bi bi-person-plus"></i> Добавить
          </Button>
        </div>
      </div>
    </Modal>
  )
}