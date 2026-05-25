import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../../app/context/AuthContext'
import Sidebar from '../../widgets/Sidebar/Sidebar'
import ModelsTable from '../../widgets/ModelsTable/ModelsTable'
import CreateModelModal from '../../features/ml-models/ui/CreateModelModal/CreateModelModal'
import EditModelModal from '../../features/ml-models/ui/EditModelModal/EditModelModal'
import PageHeader from '../../shared/ui/PageHeader/PageHeader'
import Button from '../../shared/ui/Button/Button'
import { getModels, createModel, updateModel, activateModel, deleteModel, downloadModel, addModelVersion } from '../../features/ml-models/api/modelsApi'
import { useToast } from '../../shared/hooks/useToast'
import { useModal } from '../../shared/hooks/useModal'
import ToastContainer from '../../shared/ui/Toast/ToastContainer'
import styles from './DevModelsPage.module.css'

export default function DevModelsPage() {
  const navigate = useNavigate()
  const { logout, isAuthenticated } = useAuth()
  const [models, setModels] = useState([])
  const [loading, setLoading] = useState(true)
  const [selectedModel, setSelectedModel] = useState(null)
  const { isOpen: isCreateModalOpen, openModal: openCreateModal, closeModal: closeCreateModal } = useModal()
  const { isOpen: isEditModalOpen, openModal: openEditModal, closeModal: closeEditModal } = useModal()
  const { toast, showToast, hideToast } = useToast()

  useEffect(() => {
    if (!isAuthenticated) {
      navigate('/login')
      return
    }
    loadModels()
  }, [isAuthenticated, navigate])

  const loadModels = async () => {
    setLoading(true)
    try {
      const data = await getModels()
      setModels(data)
    } catch (error) {
      showToast('Ошибка загрузки моделей', '#e0745f')
    } finally {
      setLoading(false)
    }
  }

  const handleCreateModel = async (formData) => {
    try {
      await createModel(formData)
      showToast('Модель успешно создана', '#1f7a63')
      await loadModels()
    } catch (error) {
      showToast(error.message || 'Ошибка создания модели', '#e0745f')
      throw error
    }
  }

  const handleUpdateModel = async (modelId, updateData) => {
    try {
      await updateModel(modelId, updateData)
      showToast('Модель обновлена', '#1f7a63')
      await loadModels()
    } catch (error) {
      showToast(error.message || 'Ошибка обновления модели', '#e0745f')
      throw error
    }
  }

  const handleAddVersion = async (modelId, file) => {
    try {
      await addModelVersion(modelId, file)
      showToast('Новая версия создана', '#1f7a63')
      await loadModels()
    } catch (error) {
      showToast(error.message || 'Ошибка создания версии', '#e0745f')
      throw error
    }
  }

  const handleActivateModel = async (modelId) => {
    try {
      await activateModel(modelId)
      showToast('Модель активирована', '#1f7a63')
      await loadModels()
    } catch (error) {
      showToast('Ошибка активации модели', '#e0745f')
    }
  }

  const handleDeleteModel = async (modelId, modelName) => {
    if (window.confirm(`Удалить модель "${modelName}"? Это действие необратимо.`)) {
      try {
        await deleteModel(modelId)
        showToast('Модель удалена', '#1f7a63')
        await loadModels()
      } catch (error) {
        showToast('Ошибка удаления модели', '#e0745f')
      }
    }
  }

  const handleDownloadModel = async (modelId) => {
    try {
      const result = await downloadModel(modelId)
      if (result) {
        showToast('Скачивание началось', '#1f7a63')
      }
    } catch (error) {
      showToast('Ошибка скачивания', '#e0745f')
    }
  }

  const handleEditModel = (model) => {
    setSelectedModel(model)
    openEditModal()
  }

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  return (
    <div className={styles.page}>
      <div className="bg-glow"></div>
      <div className="bg-dot-pattern"></div>
      
      <Sidebar onLogout={handleLogout} />
      
      <div className={styles.content}>
        <PageHeader 
          title="ML Модели"
          description="Управление моделями машинного обучения"
          actions={
            <Button onClick={openCreateModal} icon="bi-plus-lg">
              Создать модель
            </Button>
          }
        />

        {loading ? (
          <div className={styles.loading}>
            <i className="bi bi-hourglass-split"></i> Загрузка...
          </div>
        ) : (
          <ModelsTable 
            models={models}
            onEdit={handleEditModel}
            onActivate={handleActivateModel}
            onDelete={handleDeleteModel}
            onDownload={handleDownloadModel}
          />
        )}
      </div>

      <CreateModelModal 
        isOpen={isCreateModalOpen}
        onClose={closeCreateModal}
        onCreate={handleCreateModel}
      />

      <EditModelModal 
        isOpen={isEditModalOpen}
        onClose={closeEditModal}
        model={selectedModel}
        onSave={handleUpdateModel}
        onNewVersion={handleAddVersion}
      />

      <ToastContainer toast={toast} onHide={hideToast} />
    </div>
  )
}