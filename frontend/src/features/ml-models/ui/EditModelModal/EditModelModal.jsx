import { useState, useEffect } from 'react'
import Modal from '../../../../shared/ui/Modal/Modal'
import Button from '../../../../shared/ui/Button/Button'
import Input from '../../../../shared/ui/Input/Input'
import { architectureOptions } from '../../model/models.mock'
import styles from './EditModelModal.module.css'

export default function EditModelModal({ isOpen, onClose, model, onSave, onNewVersion }) {
  const [formData, setFormData] = useState({
    name: '',
    architecture: '',
    file: null
  })
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    if (model && isOpen) {
      setFormData({
        name: model.name,
        architecture: model.architecture,
        file: null
      })
      setError('')
    }
  }, [model, isOpen])

  const handleSubmit = async () => {
    if (!formData.name.trim()) {
      setError('Введите название модели')
      return
    }

    setLoading(true)
    setError('')
    
    try {
      // Обновляем название модели
      if (formData.name !== model.name) {
        await onSave(model.id, { name: formData.name })
      }
      
      // Если выбран файл, создаем новую версию
      if (formData.file) {
        await onNewVersion(model.id, formData.file)
      }
      
      onClose()
    } catch (err) {
      setError(err.message || 'Ошибка сохранения')
    } finally {
      setLoading(false)
    }
  }

  const handleClose = () => {
    setFormData({ name: '', architecture: '', file: null })
    setError('')
    onClose()
  }

  const formatFileSize = (bytes) => {
    if (!bytes) return ''
    const sizes = ['Б', 'КБ', 'МБ', 'ГБ']
    const i = Math.floor(Math.log(bytes) / Math.log(1024))
    return `${(bytes / Math.pow(1024, i)).toFixed(1)} ${sizes[i]}`
  }

  const getArchitectureLabel = (arch) => {
    const labels = {
      resnet50: 'ResNet50',
      efficientnet_b3: 'EfficientNet-B3',
      densenet121: 'DenseNet121'
    }
    return labels[arch] || arch
  }

  if (!model) return null

  const hasChanges = formData.name !== model.name || formData.file !== null

  return (
    <Modal isOpen={isOpen} onClose={handleClose} title="Редактирование модели">
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
          <div className={styles.architectureInfo}>
            <i className="bi bi-info-circle"></i>
            <span>{getArchitectureLabel(model.architecture)}</span>
          </div>
          <div className={styles.hint}>
            <i className="bi bi-lock-fill"></i>
            Архитектуру нельзя изменить после создания модели
          </div>
        </div>

        <div className={styles.fieldGroup}>
          <label className={styles.label}>
            <i className="bi bi-file-earmark-binary"></i>
            <span>Новая версия модели</span>
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
            {formData.file ? formData.file.name : 'Выберите файл для новой версии'}
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
            Текущая версия: v{model.current_version?.version || '1.0.0'}
          </div>
        </div>

        {error && <div className={styles.error}>{error}</div>}

        <div className={styles.actions}>
          <Button variant="secondary" onClick={handleClose}>
            Отмена
          </Button>
          <Button onClick={handleSubmit} loading={loading} disabled={!hasChanges}>
            Сохранить изменения
          </Button>
        </div>
      </div>
    </Modal>
  )
}