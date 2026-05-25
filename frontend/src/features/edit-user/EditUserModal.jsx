import { useState, useEffect } from 'react'
import Modal from '../../shared/ui/Modal/Modal'
import RolesSelector from './RolesSelector'
import BlockToggle from './BlockToggle'
import styles from './EditUserModal.module.css'

export default function EditUserModal({ isOpen, onClose, user, onSave }) {
  const [formData, setFormData] = useState({
    fullname: '',
    email: '',
    roles: [],
    blocked: false
  })

  useEffect(() => {
    if (user) {
      setFormData({
        fullname: user.fullname,
        email: user.email,
        roles: [...user.roles],
        blocked: user.blocked
      })
    }
  }, [user])

  const handleChange = (field, value) => {
    setFormData(prev => ({ ...prev, [field]: value }))
  }

  const handleSubmit = () => {
    if (!formData.fullname.trim() || !formData.email.trim()) {
      alert('Заполните имя и email')
      return
    }
    if (!formData.email.includes('@')) {
      alert('Введите корректный email')
      return
    }
    if (formData.roles.length === 0) {
      alert('Пользователь должен иметь хотя бы одну роль')
      return
    }

    onSave({
      ...user,
      ...formData
    })
  }

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="Редактирование пользователя">
      <div className={styles.formGroup}>
        <label><i className="bi bi-person"></i> Полное имя</label>
        <input 
          type="text" 
          value={formData.fullname}
          onChange={(e) => handleChange('fullname', e.target.value)}
          placeholder="Имя Фамилия"
        />
      </div>

      <div className={styles.formGroup}>
        <label><i className="bi bi-envelope"></i> Email</label>
        <input 
          type="email" 
          value={formData.email}
          onChange={(e) => handleChange('email', e.target.value)}
          placeholder="user@dermaclinic.ru"
        />
      </div>

      <div className={styles.formGroup}>
        <label><i className="bi bi-lock"></i> Статус доступа</label>
        <BlockToggle 
          blocked={formData.blocked}
          onChange={(blocked) => handleChange('blocked', blocked)}
        />
      </div>

      <div className={styles.formGroup}>
        <label><i className="bi bi-tag"></i> Роли (можно выбрать несколько)</label>
        <RolesSelector 
          selectedRoles={formData.roles}
          onChange={(roles) => handleChange('roles', roles)}
        />
      </div>

      <div className={styles.modalActions}>
        <button className={styles.btnCancel} onClick={onClose}>
          Отмена
        </button>
        <button className={styles.btnSave} onClick={handleSubmit}>
          Сохранить изменения
        </button>
      </div>
    </Modal>
  )
}