import { calculateAge } from '../../entities/patient/model/patient.helpers'
import styles from './DoctorRow.module.css'

export default function DoctorRow({ doctor, onDelete }) {
  return (
    <tr>
      <td>
        <div className={styles.userInfo}>
          <div className={styles.avatar}>
            {doctor.fullname.charAt(0).toUpperCase()}
          </div>
          <div className={styles.userName}>{doctor.fullname}</div>
        </div>
      </td>
      <td>{doctor.email}</td>
      <td>{doctor.phone || 'Не указан'}</td>
      <td>{calculateAge(doctor.birthDate)}</td>
      <td className={styles.actions}>
        <button 
          className={styles.removeBtn}
          onClick={() => onDelete(doctor.id, doctor.fullname)}
          title="Удалить"
        >
          <i className="bi bi-trash"></i>
        </button>
      </td>
    </tr>
  )
}