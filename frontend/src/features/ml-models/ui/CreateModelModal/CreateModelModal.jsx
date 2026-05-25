import { useState } from 'react'
import Modal from '../../../../shared/ui/Modal/Modal'
import Button from '../../../../shared/ui/Button/Button'
import Input from '../../../../shared/ui/Input/Input'
import { architectureOptions } from '../../model/models.mock'
import styles from './CreateModelModal.module.css'

export default function CreateModelModal({ isOpen, onClose, onCreate }) {
  const [formData, setFormData] = useState({
    name: '',
    architecture: 'resnet50',
    file: null
  })
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const handleSubmit = async () => {
    if (!formData.name.trim()) {
      setError('Введите название модели')
      return
    }
    if (!formData.file) {
      setError('Выберите файл модели')
      return
    }

    setLoading(true)
    setError('')
    
    try {
      await onCreate(formData)
      // Очищаем форму только после успешного создания
      setFormData({ name: '', architecture: 'resnet50', file: null })
      onClose()
    } catch (err) {
      setError(err.message || 'Ошибка создания модели')
    } finally {
      setLoading(false)
    }
  }

  const handleClose = () => {
    // Сбрасываем форму при закрытии
    setFormData({ name: '', architecture: 'resnet50', file: null })
    setError('')
    onClose()
  }

  const formatFileSize = (bytes) => {
    if (!bytes) return ''
    const sizes = ['Б', 'КБ', 'МБ', 'ГБ']
    const i = Math.floor(Math.log(bytes) / Math.log(1024))
    return `${(bytes / Math.pow(1024, i)).toFixed(1)} ${sizes[i]}`
  }

  return (
    <Modal isOpen={isOpen} onClose={handleClose} title="Создание модели">
      <div className={styles.container}>
        <Input
          label="Название модели"
          icon="bi-tag"
          value={formData.name}
          onChange={(e) => setFormData({ ...formData, name: e.target.value })}
          placeholder="Введите название модели"
        />

        <div className={styles.fieldGroup}>
          <label className={styles.label}>
            <i className="bi bi-cpu"></i>
            <span>Архитектура</span>
          </label>
          <select
            className={styles.select}
            value={formData.architecture}
            onChange={(e) => setFormData({ ...formData, architecture: e.target.value })}
          >
            {architectureOptions.map(opt => (
              <option key={opt.value} value={opt.value}>
                {opt.label}
              </option>
            ))}
          </select>
          <div className={styles.hint}>
            <i className="bi bi-info-circle"></i>
            {architectureOptions.find(opt => opt.value === formData.architecture)?.description}
          </div>
        </div>

        <div className={styles.fieldGroup}>
          <label className={styles.label}>
            <i className="bi bi-file-earmark-binary"></i>
            <span>Файл модели</span>
          </label>
          <input
            type="file"
            id="modelFile"
            accept=".pt,.pth,.onnx"
            onChange={(e) => setFormData({ ...formData, file: e.target.files[0] })}
            className={styles.fileInput}
          />
          <label htmlFor="modelFile" className={styles.fileLabel}>
            <i className="bi bi-cloud-arrow-up"></i>
            {formData.file ? formData.file.name : 'Нажмите или перетащите файл'}
          </label>
          {formData.file && (
            <div className={styles.fileInfo}>
              <i className="bi bi-file-earmark"></i>
              <span>{formData.file.name}</span>
              <span className={styles.fileSize}>({formatFileSize(formData.file.size)})</span>
              <button 
                className={styles.clearFile}
                onClick={() => setFormData({ ...formData, file: null })}
              >
                <i className="bi bi-x-lg"></i>
              </button>
            </div>
          )}
          <div className={styles.hint}>
            <i className="bi bi-info-circle"></i>
            Поддерживаемые форматы: .pt, .pth, .onnx
          </div>
        </div>

        {error && <div className={styles.error}>{error}</div>}

        <div className={styles.actions}>
          <Button variant="secondary" onClick={handleClose}>
            Отмена
          </Button>
          <Button onClick={handleSubmit} loading={loading} disabled={!formData.file || !formData.name}>
            Создать модель
          </Button>
        </div>
      </div>
    </Modal>
  )
}