import PredictionRow from './PredictionRow'
import styles from './PredictionsTable.module.css'

export default function PredictionsTable({ predictions, onViewDetails }) {
  if (!predictions || !Array.isArray(predictions) || predictions.length === 0) {
    return (
      <div className={styles.card}>
        <table className={styles.table}>
          <thead>
            <tr>
              <th>Дата</th>
              <th>Доброкачественность</th>
              <th>Меланома</th>
              <th>Диагноз</th>
              <th>Вероятность</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            <tr className={styles.emptyRow}>
              <td colSpan="6">
                <div className={styles.emptyState}>
                  <i className="bi bi-inbox"></i>
                  <p>История предсказаний пуста</p>
                  <span>Вы еще не делали ни одного анализа</span>
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
            <th>Дата</th>
            <th>Доброкачественность</th>
            <th>Меланома</th>
            <th>Диагноз</th>
            <th>Вероятность</th>
            <th>Действия</th>
          </tr>
        </thead>
        <tbody>
          {predictions.map((prediction, index) => (
            <PredictionRow 
              key={prediction.id || index}
              prediction={prediction}
              onViewDetails={onViewDetails}
            />
          ))}
        </tbody>
      </table>
    </div>
  )
}