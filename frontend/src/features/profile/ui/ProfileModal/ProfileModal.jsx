import { useState, useEffect } from 'react'
import Modal from '../../../../shared/ui/Modal/Modal'
import Button from '../../../../shared/ui/Button/Button'
import { updateCurrentUser, getCurrentUser } from '../../../users/api/usersApi'
import { useAuth } from '../../../../app/context/AuthContext'
import { useToast } from '../../../../shared/hooks/useToast'
import styles from './ProfileModal.module.css'

export default function ProfileModal({ isOpen, onClose, onSave, userData }) {
  const [formData, setFormData] = useState({
    firstName: '',
    lastName: '',
    patronymic: '',
    phone: '',
    email: '',
    birthDate: '',
  })
  const [loading, setLoading] = useState(false)
  const { updateUserProfile } = useAuth()
  const { showToast } = useToast()

  useEffect(() => {
    if (isOpen && userData) {
      setFormData({
        firstName: userData.firstName || '',
        lastName: userData.lastName || '',
        patronymic: userData.middleName || '',
        phone: userData.phone || '',
        email: userData.email || '',
        birthDate: userData.birthDate || '',
      })
    }
  }, [isOpen, userData])

  const handleChange = (field, value) => {
    setFormData(prev => ({ ...prev, [field]: value }))
  }

  const handleSubmit = async () => {
    setLoading(true)
    try {
      const updateData = {
        first_name: formData.firstName,
        last_name: formData.lastName,
        middle_name: formData.patronymic,
        phone: formData.phone,
        birth_date: formData.birthDate || null,
      }
      
      // Вызываем updateUserProfile из контекста
      const result = await updateUserProfile(updateData)
      
      if (result.success) {
        showToast('Личная информация сохранена', '#1f7a63')
        onClose()
      } else {
        showToast(result.error || 'Ошибка сохранения', '#e0745f')
      }
    } catch (error) {
      showToast(error.message || 'Ошибка сохранения', '#e0745f')
    } finally {
      setLoading(false)
    }
  }

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="Редактирование профиля">
      <div className={styles.modalContent}>
        {/* Блок ФИО */}
        <div className={styles.fullnameBlock}>
          <div className={styles.fieldGroup}>
            <label className={styles.label}>
              <i className="bi bi-person"></i>
              <span>Имя</span>
            </label>
            <input
              type="text"
              className={styles.input}
              value={formData.firstName}
              onChange={(e) => handleChange('firstName', e.target.value)}
              placeholder="Введите имя"
            />
          </div>
          
          <div className={styles.fieldGroup}>
            <label className={styles.label}>
              <i className="bi bi-person-badge"></i>
              <span>Фамилия</span>
            </label>
            <input
              type="text"
              className={styles.input}
              value={formData.lastName}
              onChange={(e) => handleChange('lastName', e.target.value)}
              placeholder="Введите фамилию"
            />
          </div>
          
          <div className={styles.fieldGroup}>
            <label className={styles.label}>
              <i className="bi bi-person-vcard"></i>
              <span>Отчество</span>
            </label>
            <input
              type="text"
              className={styles.input}
              value={formData.patronymic}
              onChange={(e) => handleChange('patronymic', e.target.value)}
              placeholder="Введите отчество"
            />
          </div>
        </div>

        {/* Две колонки */}
        <div className={styles.twoColumns}>
          <div className={styles.column}>
            <div className={styles.fieldGroup}>
              <label className={styles.label}>
                <i className="bi bi-telephone"></i>
                <span>Телефон</span>
              </label>
              <input
                type="tel"
                className={styles.input}
                value={formData.phone}
                onChange={(e) => handleChange('phone', e.target.value)}
                placeholder="+7 (xxx) xxx-xx-xx"
              />
            </div>
            
            <div className={styles.fieldGroup}>
              <label className={styles.label}>
                <i className="bi bi-envelope"></i>
                <span>Email</span>
              </label>
              <input
                type="email"
                className={styles.input}
                value={formData.email}
                readOnly
                disabled
              />
              <div className={styles.hint}>Email нельзя изменить</div>
            </div>
          </div>

          <div className={styles.column}>
            <div className={styles.fieldGroup}>
              <label className={styles.label}>
                <i className="bi bi-calendar"></i>
                <span>Дата рождения</span>
              </label>
              <input
                type="date"
                className={styles.input}
                value={formData.birthDate}
                onChange={(e) => handleChange('birthDate', e.target.value)}
              />
            </div>
          </div>
        </div>

        <div className={styles.actions}>
          <Button variant="secondary" onClick={onClose}>
            Отмена
          </Button>
          <Button onClick={handleSubmit} loading={loading}>
            <i className="bi bi-check-lg"></i> Сохранить изменения
          </Button>
        </div>
      </div>
    </Modal>
  )
}