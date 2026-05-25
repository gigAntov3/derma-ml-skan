import { useState, useEffect, useCallback } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { useAuth } from '../../app/context/AuthContext'
import Sidebar from '../../widgets/Sidebar/Sidebar'
import Button from '../../shared/ui/Button/Button'
import PredictionsTable from '../../widgets/PredictionsTable/PredictionsTable'
import PredictionDetailsModal from '../../features/predictions/ui/PredictionDetailsModal/PredictionDetailsModal'
import { 
  getPatientById, 
  getPatientPredictionsForDoctor,
  getPatientRecommendation,
  updatePatientRecommendation 
} from '../../features/patients/api/patientsApi'
import { useToast } from '../../shared/hooks/useToast'
import { useModal } from '../../shared/hooks/useModal'
import ToastContainer from '../../shared/ui/Toast/ToastContainer'
import styles from './DoctorPatientDetailPage.module.css'

export default function DoctorPatientDetailPage() {
  const { id } = useParams()
  const navigate = useNavigate()
  const { logout, isAuthenticated, user } = useAuth()
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [patient, setPatient] = useState(null)
  const [predictions, setPredictions] = useState([])
  const [selectedPrediction, setSelectedPrediction] = useState(null)
  
  // Состояния для врачебного заключения
  const [doctorDiagnosis, setDoctorDiagnosis] = useState('')
  const [doctorRecommendation, setDoctorRecommendation] = useState('')
  const [recommendationId, setRecommendationId] = useState(null)
  const [hasExistingRecommendation, setHasExistingRecommendation] = useState(false)
  const [loadingRecommendation, setLoadingRecommendation] = useState(false)
  
  const { isOpen: isModalOpen, openModal, closeModal } = useModal()
  const { toast, showToast, hideToast } = useToast()

  // Загрузка рекомендаций - выносим в отдельную функцию
  const loadRecommendation = useCallback(async () => {
    if (!id) return
    
    setLoadingRecommendation(true)
    try {
      const recommendation = await getPatientRecommendation(id)
      console.log('Loaded recommendation:', recommendation) // Для отладки
      
      if (recommendation) {
        setDoctorDiagnosis(recommendation.diagnosis || '')
        setDoctorRecommendation(recommendation.recommendations || '')
        setRecommendationId(recommendation.id)
        setHasExistingRecommendation(true)
      } else {
        // Нет существующего заключения
        setDoctorDiagnosis('')
        setDoctorRecommendation('')
        setRecommendationId(null)
        setHasExistingRecommendation(false)
      }
    } catch (error) {
      console.error('Error loading recommendation:', error)
      // Если 404 - просто нет заключения, не показываем ошибку
      if (error.response?.status !== 404) {
        showToast('Ошибка загрузки заключения', '#e0745f')
      }
      // Сбрасываем поля
      setDoctorDiagnosis('')
      setDoctorRecommendation('')
      setRecommendationId(null)
      setHasExistingRecommendation(false)
    } finally {
      setLoadingRecommendation(false)
    }
  }, [id, showToast])

  const loadData = useCallback(async () => {
    setLoading(true)
    try {
      // Загружаем данные пациента
      const patientData = await getPatientById(id)
      setPatient({
        id: patientData.id,
        fullname: `${patientData.last_name} ${patientData.first_name} ${patientData.middle_name || ''}`.trim(),
        email: patientData.email,
        phone: patientData.phone || 'Не указан',
        birthDate: patientData.birth_date,
      })

      // Загружаем историю предсказаний
      const historyData = await getPatientPredictionsForDoctor(id)
      const formattedPredictions = (historyData.predictions || []).map(pred => ({
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
      
      // Загружаем врачебное заключение
      await loadRecommendation()
      
    } catch (error) {
      console.error('Error loading data:', error)
      showToast(error.message || 'Ошибка загрузки данных', '#e0745f')
    } finally {
      setLoading(false)
    }
  }, [id, loadRecommendation, showToast])

  useEffect(() => {
    if (!isAuthenticated) {
      navigate('/login')
      return
    }
    // Проверяем, что пользователь - врач
    if (user && !user.roles?.includes('doctor')) {
      navigate('/patient/doctors')
      return
    }
    loadData()
  }, [isAuthenticated, navigate, id, user, loadData])

  const handleViewDetails = (predictionId) => {
    const prediction = predictions.find(p => p.id === predictionId)
    setSelectedPrediction(prediction)
    openModal()
  }

  const handleSaveDiagnosis = async () => {
    // Проверяем, что заполнены оба поля
    if (!doctorDiagnosis.trim() && !doctorRecommendation.trim()) {
      showToast('Заполните хотя бы одно поле (диагноз или рекомендации)', '#e0745f')
      return
    }

    setSaving(true)
    try {
      // Подготавливаем данные для отправки
      const updateData = {}
      if (doctorDiagnosis.trim()) {
        updateData.diagnosis = doctorDiagnosis.trim()
      }
      if (doctorRecommendation.trim()) {
        updateData.recommendations = doctorRecommendation.trim()
      }
      
      console.log('Saving recommendation:', updateData) // Для отладки
      
      // Отправляем на сервер
      const result = await updatePatientRecommendation(id, updateData)
      
      console.log('Saved recommendation result:', result) // Для отладки
      
      // Обновляем локальное состояние из ответа сервера
      if (result) {
        setDoctorDiagnosis(result.diagnosis || '')
        setDoctorRecommendation(result.recommendations || '')
        setRecommendationId(result.id)
        setHasExistingRecommendation(true)
      }
      
      showToast('Диагноз и рекомендации сохранены', '#1f7a63')
      
    } catch (error) {
      console.error('Error saving recommendation:', error)
      showToast(error.response?.data?.detail || 'Ошибка сохранения', '#e0745f')
    } finally {
      setSaving(false)
    }
  }

  const handleAddAnalysis = () => {
    navigate(`/doctor/patients/${id}/analyse`)
  }

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  // Отображение загрузки
  if (loading) {
    return (
      <div className={styles.page}>
        <Sidebar onLogout={handleLogout} />
        <div className={styles.content}>
          <div className={styles.loading}>Загрузка...</div>
        </div>
      </div>
    )
  }

  // Отображение если пациент не найден
  if (!patient) {
    return (
      <div className={styles.page}>
        <Sidebar onLogout={handleLogout} />
        <div className={styles.content}>
          <div className={styles.notFound}>
            <i className="bi bi-person-x"></i>
            <p>Пациент не найден</p>
            <Button onClick={() => navigate('/doctor/patients')}>
              Вернуться к списку
            </Button>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className={styles.page}>
      <div className="bg-glow"></div>
      <div className="bg-dot-pattern"></div>

      <Sidebar onLogout={handleLogout} />

      <div className={styles.content}>
        {/* Карточка пациента */}
        <div className={styles.patientCard}>
          <div className={styles.patientInfo}>
            <div className={styles.patientAvatar}>
              {patient.fullname.charAt(0).toUpperCase()}
            </div>
            <div>
              <h1>{patient.fullname}</h1>
              <div className={styles.patientDetails}>
                <span><i className="bi bi-envelope"></i> {patient.email}</span>
                <span><i className="bi bi-telephone"></i> {patient.phone}</span>
                <span><i className="bi bi-calendar"></i> ID: {patient.id}</span>
              </div>
            </div>
          </div>
        </div>

        {/* Врачебное заключение */}
        <div className={styles.doctorSection}>
          <div className={styles.sectionHeader}>
            <div className={styles.headerLeft}>
              <i className="bi bi-clipboard-heart"></i>
              <h3>Врачебное заключение</h3>
            </div>
            <button 
              className={styles.actionBtn} 
              onClick={handleSaveDiagnosis} 
              disabled={saving}
            >
              {saving ? (
                <>
                  <i className="bi bi-hourglass-split"></i>
                  Сохранение...
                </>
              ) : (
                <>
                  <i className="bi bi-save"></i>
                  Сохранить
                </>
              )}
            </button>
          </div>
          <div className={styles.doctorCard}>
            <div className={styles.formGroup}>
              <label>
                Диагноз
                {!doctorDiagnosis && <span className={styles.optional}>(необязательно)</span>}
              </label>
              <textarea
                className={styles.textarea}
                rows="3"
                placeholder="Введите клинический диагноз..."
                value={doctorDiagnosis || ''}
                onChange={(e) => setDoctorDiagnosis(e.target.value)}
              />
            </div>
            <div className={styles.formGroup}>
              <label>
                Рекомендации
                {!doctorRecommendation && <span className={styles.optional}>(необязательно)</span>}
              </label>
              <textarea
                className={styles.textarea}
                rows="4"
                placeholder="Введите рекомендации для пациента..."
                value={doctorRecommendation || ''}
                onChange={(e) => setDoctorRecommendation(e.target.value)}
              />
            </div>
          </div>
        </div>

        {/* История анализов */}
        <div className={styles.historySection}>
          <div className={styles.sectionHeader}>
            <div className={styles.headerLeft}>
              <i className="bi bi-clock-history"></i>
              <h3>История анализов</h3>
              <span className={styles.count}>{predictions.length} анализов</span>
            </div>
            <button className={styles.actionBtn} onClick={handleAddAnalysis}>
              <i className="bi bi-plus-lg"></i> Добавить анализ
            </button>
          </div>
          <PredictionsTable 
            predictions={predictions}
            onViewDetails={handleViewDetails}
          />
        </div>
      </div>

      {/* Модальное окно с деталями анализа */}
      <PredictionDetailsModal 
        isOpen={isModalOpen}
        onClose={closeModal}
        prediction={selectedPrediction}
      />

      <ToastContainer toast={toast} onHide={hideToast} />
    </div>
  )
}