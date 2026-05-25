import styles from './PredictionsTable.module.css'

const formatDate = (dateString) => {
  if (!dateString) return 'Дата неизвестна'
  try {
    const date = new Date(dateString)
    return date.toLocaleDateString('ru-RU', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric'
    })
  } catch {
    return 'Дата неизвестна'
  }
}

const getDiagnosisLabel = (diagnosisCode) => {
  if (!diagnosisCode) return 'Не определен'
  const labels = {
    melanoma: 'Меланома',
    nevus: 'Невус',
    basal_cell_carcinoma: 'Базалиома',
    actinic_keratosis: 'Актинический кератоз'
  }
  return labels[diagnosisCode] || diagnosisCode
}

export default function PredictionRow({ prediction, onViewDetails }) {
  if (!prediction) return null
  
  const diagnosisCode = prediction.diagnosis?.detected
  const diagnosisLabel = getDiagnosisLabel(diagnosisCode)
  const isMalignant = prediction.malignant?.detected || false
  const hasMelanoma = prediction.melanoma?.detected || false
  
  // Вероятность для выявленного диагноза
  let diagnosisProbability = 0
  if (diagnosisCode && prediction.diagnosis?.probabilities) {
    diagnosisProbability = (prediction.diagnosis.probabilities[diagnosisCode] || 0) * 100
  }

  return (
    <tr>
      <td>{formatDate(prediction.created_at)}</td>
      <td>
        <span className={`${styles.diagnosisBadge} ${isMalignant ? styles.malignant : styles.benign}`}>
          <i className={`bi ${isMalignant ? 'bi-exclamation-triangle-fill' : 'bi-check-circle-fill'}`}></i>
          {isMalignant ? 'Злокачественное' : 'Доброкачественное'}
        </span>
       </td>
      <td>
        <span className={`${styles.diagnosisBadge} ${hasMelanoma ? styles.malignant : styles.benign}`}>
          <i className={`bi ${hasMelanoma ? 'bi-exclamation-triangle-fill' : 'bi-check-circle-fill'}`}></i>
          {hasMelanoma ? 'Обнаружена' : 'Не обнаружена'}
        </span>
       </td>
      <td>
        <span className={`${styles.diagnosisBadge} ${isMalignant ? styles.malignant : styles.benign}`}>
          <i className="bi bi-clipboard-heart"></i>
          {diagnosisLabel}
        </span>
       </td>
      <td>
        <div className={styles.confidenceBar}>
          <div className={styles.bar}>
            <div 
              className={`${styles.barFill} ${isMalignant ? styles.high : styles.success}`}
              style={{ width: `${diagnosisProbability}%` }}
            />
          </div>
          <span className={styles.confidenceValue}>{Math.round(diagnosisProbability)}%</span>
        </div>
       </td>
      <td>
        <button 
          className={styles.viewBtn}
          onClick={() => onViewDetails(prediction.id)}
          title="Детали"
        >
          <i className="bi bi-eye"></i>
        </button>
       </td>
    </tr>
  )
}