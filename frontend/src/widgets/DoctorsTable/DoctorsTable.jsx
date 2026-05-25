import DoctorRow from './DoctorRow'
import styles from './DoctorsTable.module.css'

export default function DoctorsTable({ doctors, onDeleteDoctor }) {
  if (doctors.length === 0) {
    return (
      <div className={styles.card}>
        <table className={styles.table}>
          <thead>
            <tr>
              <th>Врач</th>
              <th>Email</th>
              <th>Телефон</th>
              <th>Возраст</th>
              <th>Действия</th>
            </tr>
          </thead>
          <tbody>
            <tr className={styles.emptyRow}>
              <td colSpan="5">
                <div className={styles.emptyState}>
                  <i className="bi bi-inbox"></i>
                  <p>У вас пока нет врачей</p>
                  <span>Добавьте первого врача</span>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    )
  }

  return (
    <div className={styles.card}>
      <table className={styles.table}>
        <thead>
          <tr>
            <th>Врач</th>
            <th>Email</th>
            <th>Телефон</th>
            <th>Возраст</th>
            <th>Действия</th>
          </tr>
        </thead>
        <tbody>
          {doctors.map(doctor => (
            <DoctorRow 
              key={doctor.id}
              doctor={doctor}
              onDelete={onDeleteDoctor}
            />
          ))}
        </tbody>
      </table>
    </div>
  )
}