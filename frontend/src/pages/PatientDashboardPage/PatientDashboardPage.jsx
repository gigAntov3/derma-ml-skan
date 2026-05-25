import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../../app/context/AuthContext'
import PageHeader from '../../shared/ui/PageHeader/PageHeader'
import Sidebar from '../../widgets/Sidebar/Sidebar'
import ToastContainer from '../../shared/ui/Toast/ToastContainer'
import { useToast } from '../../shared/hooks/useToast'
import { getCurrentUser } from '../../features/users/api/usersApi'
import { getMyRecommendation } from '../../features/doctors/api/doctorsApi'
import styles from './PatientDashboardPage.module.css'

export default function PatientDashboardPage() {
  const navigate = useNavigate()
  const { logout, isAuthenticated } = useAuth()
  const [loading, setLoading] = useState(true)
  const [patient, setPatient] = useState(null)
  const [diagnosis, setDiagnosis] = useState(null)
  const { toast, showToast, hideToast } = useToast()

  useEffect(() => {
    if (!isAuthenticated) {
      navigate('/login')
      return
    }
    loadData()
  }, [isAuthenticated, navigate])

  const loadData = async () => {
    setLoading(true)
    try {
      const profile = await getCurrentUser()
      setPatient({
        fullname: `${profile.last_name} ${profile.first_name} ${profile.middle_name || ''}`.trim(),
        email: profile.email,
        phone: profile.phone || 'Не указан',
      })

      const diagnosisData = await getMyRecommendation()
      if (diagnosisData && diagnosisData.diagnosis) {
        setDiagnosis(diagnosisData)
      } else {
        setDiagnosis(null)
      }
    } catch (error) {
      console.error('Error:', error)
      showToast('Ошибка загрузки данных', '#e0745f')
    } finally {
      setLoading(false)
    }
  }

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  const formatDate = (dateString) => {
    if (!dateString) return '—'
    const date = new Date(dateString)
    return date.toLocaleDateString('ru-RU', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    })
  }

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

  return (
    <div className={styles.page}>
      <Sidebar onLogout={handleLogout} />
      
      <div className={styles.content}>
        <PageHeader 
          title="Мой диагноз"
          description="Врачебное заключение и рекомендации"
        />

        {diagnosis && diagnosis.diagnosis ? (
          <div className={styles.diagnosisCard}>
            <div className={styles.cardHeader}>
              <div className={styles.cardHeaderLeft}>
                <i className="bi bi-file-medical"></i>
                <h3>Клинический диагноз</h3>
              </div>
              <div className={styles.cardDate}>
                <i className="bi bi-calendar3"></i>
                {formatDate(diagnosis.created_at)}
              </div>
            </div>
            
            <div className={styles.diagnosisBlock}>
              <label>
                <i className="bi bi-stethoscope"></i>
                Диагноз
              </label>
              <div className={styles.diagnosisText}>
                {diagnosis.diagnosis}
              </div>
            </div>

            {diagnosis.recommendations && (
              <div className={styles.recommendationsBlock}>
                <label>
                <i className="bi bi-stethoscope"></i>
                  Рекомендации
                </label>
                <div className={styles.recommendationsText}>
                  {diagnosis.recommendations}
                </div>
              </div>
            )}
          </div>
        ) : (
          <div className={styles.emptyState}>
            <i className="bi bi-clipboard-x"></i>
            <h3>Диагноз отсутствует</h3>
            <p>Врач еще не добавил диагноз</p>
          </div>
        )}
      </div>

      <ToastContainer toast={toast} onHide={hideToast} />
    </div>
  )
}