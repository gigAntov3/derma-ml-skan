import { useState, useEffect, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../../app/context/AuthContext'
import Sidebar from '../../widgets/Sidebar/Sidebar'
import PatientsTable from '../../widgets/PatientsTable/PatientsTable'
import AddPatientModal from '../../features/patients/ui/AddPatientModal/AddPatientModal'
import PageHeader from '../../shared/ui/PageHeader/PageHeader'
import Button from '../../shared/ui/Button/Button'
import { getDoctorPatients, addPatientToDoctor, removePatientFromDoctor } from '../../features/patients/api/patientsApi'
import { useToast } from '../../shared/hooks/useToast'
import { useModal } from '../../shared/hooks/useModal'
import ToastContainer from '../../shared/ui/Toast/ToastContainer'
import styles from './DoctorPatientsPage.module.css'

export default function DoctorPatientsPage() {
  const navigate = useNavigate()
  const { user, logout, isAuthenticated } = useAuth()
  const [patients, setPatients] = useState([])
  const [loading, setLoading] = useState(true)
  const { isOpen: isModalOpen, openModal: openAddModal, closeModal } = useModal()
  const { toast, showToast, hideToast } = useToast()

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
    loadPatients()
  }, [user, isAuthenticated, navigate])

  const loadPatients = async () => {
    setLoading(true)
    try {
      const data = await getDoctorPatients()
      // Преобразуем данные из API в формат для таблицы
      const formattedPatients = data.map(patient => ({
        id: patient.id,
        fullname: `${patient.last_name} ${patient.first_name} ${patient.middle_name || ''}`.trim(),
        email: patient.email,
        phone: patient.phone || 'Не указан',
        birthDate: patient.birth_date,
        registered: patient.created_at ? new Date(patient.created_at).toISOString().split('T')[0] : 'Нет данных',
      }))
      setPatients(formattedPatients)
    } catch (error) {
      showToast(error.message || 'Ошибка загрузки пациентов', '#e0745f')
    } finally {
      setLoading(false)
    }
  }

  const handleAddPatient = async (email) => {
    try {
      await addPatientToDoctor(email)
      showToast('Пациент успешно добавлен', '#1f7a63')
      await loadPatients()
      return Promise.resolve()
    } catch (error) {
      const errorMessage = error.message || 'Ошибка добавления пациента'
      showToast(errorMessage, '#e0745f')
      throw error
    }
  }

  const handleDeletePatient = async (patientId, patientName) => {
    if (window.confirm(`Удалить пациента "${patientName}" из списка?`)) {
      try {
        await removePatientFromDoctor(patientId)
        showToast('Пациент удален', '#1f7a63')
        await loadPatients()
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
          title="Мои пациенты"
          description="Управление списком ваших пациентов"
          actions={
            <Button onClick={openAddModal} icon="bi-person-plus">
              Добавить пациента
            </Button>
          }
        />

        {loading ? (
          <div className={styles.loading}>
            <i className="bi bi-hourglass-split"></i> Загрузка...
          </div>
        ) : (
          <PatientsTable 
            patients={patients} 
            onDeletePatient={handleDeletePatient}
            onViewPatient={(patientId) => navigate(`/doctor/patients/${patientId}`)}
          />
        )}
      </div>

      <AddPatientModal 
        isOpen={isModalOpen}
        onClose={closeModal}
        onAdd={handleAddPatient}
      />

      <ToastContainer toast={toast} onHide={hideToast} />
    </div>
  )
}