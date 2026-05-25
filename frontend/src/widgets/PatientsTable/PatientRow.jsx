import { useNavigate } from 'react-router-dom'
import { calculateAge } from '../../entities/patient/model/patient.helpers'
import styles from './PatientRow.module.css'

export default function PatientRow({ patient, onDelete }) {
  const navigate = useNavigate()

  const handleViewClick = () => {
    navigate(`/doctor/patients/${patient.id}`)
  }

  const handleDeleteClick = (e) => {
    e.stopPropagation()
    onDelete(patient.id, patient.fullname)
  }

  return (
    <tr className={styles.patientRow}>
      <td>
        <div className={styles.userInfo}>
          <div className={styles.avatar}>
            {patient.fullname.charAt(0).toUpperCase()}
          </div>
          <div className={styles.userName}>{patient.fullname}</div>
        </div>
      </td>
      <td>{patient.email}</td>
      <td>{patient.phone || 'Не указан'}</td>
      <td>{calculateAge(patient.birthDate)}</td>
      <td>{patient.registered || 'Нет данных'}</td>
      <td className={styles.actions}>
        <button 
          className={styles.viewBtn}
          onClick={handleViewClick}
          title="Просмотреть"
        >
          <i className="bi bi-eye"></i>
        </button>
        <button 
          className={styles.removeBtn}
          onClick={handleDeleteClick}
          title="Удалить"
        >
          <i className="bi bi-trash"></i>
        </button>
       </td>
    </tr>
  )
}