import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../../app/context/AuthContext'
import Sidebar from '../../widgets/Sidebar/Sidebar'
import PredictionsTable from '../../widgets/PredictionsTable/PredictionsTable'
import PredictionDetailsModal from '../../features/predictions/ui/PredictionDetailsModal/PredictionDetailsModal'
import PageHeader from '../../shared/ui/PageHeader/PageHeader'
import { getMyPredictionHistory, getPredictionDetails } from '../../features/doctors/api/doctorsApi'
import { useToast } from '../../shared/hooks/useToast'
import { useModal } from '../../shared/hooks/useModal'
import ToastContainer from '../../shared/ui/Toast/ToastContainer'
import styles from './PatientHistoryPage.module.css'

export default function PatientHistoryPage() {
  const navigate = useNavigate()
  const { logout, isAuthenticated, user } = useAuth()
  const [predictions, setPredictions] = useState([])
  const [loading, setLoading] = useState(true)
  const [total, setTotal] = useState(0)
  const [selectedPrediction, setSelectedPrediction] = useState(null)
  const { isOpen: isDetailsModalOpen, openModal: openDetailsModal, closeModal: closeDetailsModal } = useModal()
  const { toast, showToast, hideToast } = useToast()

  useEffect(() => {
    if (!isAuthenticated) {
      navigate('/login')
      return
    }
    // Проверяем, что пользователь - пациент
    if (user && !user.roles?.includes('patient')) {
      if (user.roles?.includes('admin')) navigate('/admin/users')
      else if (user.roles?.includes('doctor')) navigate('/doctor/patients')
      return
    }
    loadHistory()
  }, [isAuthenticated, navigate, user])

  const loadHistory = async () => {
    setLoading(true)
    try {
      const data = await getMyPredictionHistory()
      console.log('Loaded predictions data:', data)
      
      // Преобразуем данные из API в формат для таблицы
      const formattedPredictions = data.predictions.map(pred => ({
        id: pred.id,
        created_at: pred.created_at,
        image_url: pred.image_url,
        heatmap_url: pred.heatmap_url,
        model: pred.model,
        malignant: pred.malignant,
        melanoma: pred.melanoma,
        diagnosis: pred.diagnosis,
      }))
      
      setPredictions(formattedPredictions)
      setTotal(data.total)
    } catch (error) {
      showToast(error.message || 'Ошибка загрузки истории', '#e0745f')
    } finally {
      setLoading(false)
    }
  }

  const handleViewDetails = async (predictionId) => {
    try {
      const prediction = await getPredictionDetails(predictionId)
      setSelectedPrediction(prediction)
      openDetailsModal()
    } catch (error) {
      showToast(error.message || 'Ошибка загрузки деталей', '#e0745f')
    }
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
          title="История анализов"
          description={`Результаты всех ваших дерматологических исследований (${total} анализов)`}
        />

        {loading ? (
          <div className={styles.loading}>
            <i className="bi bi-hourglass-split"></i> Загрузка...
          </div>
        ) : (
          <PredictionsTable 
            predictions={predictions}
            onViewDetails={handleViewDetails}
          />
        )}
      </div>

      <PredictionDetailsModal 
        isOpen={isDetailsModalOpen}
        onClose={closeDetailsModal}
        prediction={selectedPrediction}
      />

      <ToastContainer toast={toast} onHide={hideToast} />
    </div>
  )
}