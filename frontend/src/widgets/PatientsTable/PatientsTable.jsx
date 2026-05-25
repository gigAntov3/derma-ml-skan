import PatientRow from './PatientRow'
import styles from './PatientsTable.module.css'

export default function PatientsTable({ patients, onDeletePatient }) {
  if (patients.length === 0) {
    return (
      <div className={styles.card}>
        <table className={styles.table}>
          <thead>
            <tr>
              <th>Пациент</th>
              <th>Email</th>
              <th>Телефон</th>
              <th>Возраст</th>
              <th>Дата добавления</th>
              <th>Действия</th>
            </tr>
          </thead>
          <tbody>
            <tr className={styles.emptyRow}>
              <td colSpan="6">
                <div className={styles.emptyState}>
                  <i className="bi bi-inbox"></i>
                  <p>У вас пока нет пациентов</p>
                  <span>Добавьте первого пациента</span>
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
            <th>Пациент</th>
            <th>Email</th>
            <th>Телефон</th>
            <th>Возраст</th>
            <th>Дата добавления</th>
            <th>Действия</th>
          </tr>
        </thead>
        <tbody>
          {patients.map(patient => (
            <PatientRow 
              key={patient.id}
              patient={patient}
              onDelete={onDeletePatient}
            />
          ))}
        </tbody>
      </table>
    </div>
  )
}