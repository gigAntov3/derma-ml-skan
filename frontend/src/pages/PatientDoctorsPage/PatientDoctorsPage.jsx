import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../../app/context/AuthContext'
import Sidebar from '../../widgets/Sidebar/Sidebar'
import DoctorsTable from '../../widgets/DoctorsTable/DoctorsTable'
import PageHeader from '../../shared/ui/PageHeader/PageHeader'
import { getMyDoctors, removeDoctor } from '../../features/doctors/api/doctorsApi'
import { useToast } from '../../shared/hooks/useToast'
import ToastContainer from '../../shared/ui/Toast/ToastContainer'
import styles from './PatientDoctorsPage.module.css'

export default function PatientDoctorsPage() {
  const navigate = useNavigate()
  const { user, logout, isAuthenticated } = useAuth()
  const [doctors, setDoctors] = useState([])
  const [loading, setLoading] = useState(true)
  const { toast, showToast, hideToast } = useToast()

  useEffect(() => {
    if (!isAuthenticated) {
      navigate('/login')
      return
    }
    loadDoctors()
  }, [user, isAuthenticated, navigate])

  const loadDoctors = async () => {
    setLoading(true)
    try {
      // Не передаем email, API определит текущего пользователя по токену
      const data = await getMyDoctors()
      // Преобразуем данные из API в формат для таблицы
      const formattedDoctors = data.map(doctor => ({
        id: doctor.id,
        fullname: `${doctor.last_name} ${doctor.first_name} ${doctor.middle_name || ''}`.trim(),
        email: doctor.email,
        phone: doctor.phone || 'Не указан',
        specialty: doctor.specialty || 'Дерматолог',
        experience: doctor.experience || null,
      }))
      setDoctors(formattedDoctors)
    } catch (error) {
      showToast(error.message || 'Ошибка загрузки врачей', '#e0745f')
    } finally {
      setLoading(false)
    }
  }

  const handleAddDoctor = async (email) => {
    try {
      // Не передаем email пациента, API определит по токену
      await addDoctorToPatient(email)
      showToast('Врач успешно добавлен', '#1f7a63')
      await loadDoctors()
      return Promise.resolve()
    } catch (error) {
      showToast(error.message || 'Ошибка добавления врача', '#e0745f')
      throw error
    }
  }

  const handleDeleteDoctor = async (doctorId, doctorName) => {
    if (window.confirm(`Удалить врача "${doctorName}" из списка?`)) {
      try {
        // Не передаем email пациента, API определит по токену
        await removeDoctor(doctorId)
        showToast('Врач удален', '#1f7a63')
        await loadDoctors()
      } catch (error) {
        showToast(error.message || 'Ошибка удаления', '#e0745f')
      }
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
          title="Мои врачи"
          description="Управление списком ваших лечащих врачей"
        />

        {loading ? (
          <div className={styles.loading}>
            <i className="bi bi-hourglass-split"></i> Загрузка...
          </div>
        ) : (
          <DoctorsTable 
            doctors={doctors} 
            onDeleteDoctor={handleDeleteDoctor}
          />
        )}
      </div>

      <ToastContainer toast={toast} onHide={hideToast} />
    </div>
  )
}