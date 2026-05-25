import ModelRow from './ModelRow'
import styles from './ModelsTable.module.css'

export default function ModelsTable({ models, onEdit, onActivate, onDelete, onDownload }) {
  if (models.length === 0) {
    return (
      <div className={styles.card}>
        <table className={styles.table}>
          <thead>
            <tr>
              <th>Название</th>
              <th>Архитектура</th>
              <th>Версия</th>
              <th>Статус</th>
              <th>Размер</th>
              <th>Обновлена</th>
              <th>Действия</th>
            </tr>
          </thead>
          <tbody>
            <tr className={styles.emptyRow}>
              <td colSpan="7">
                <div className={styles.emptyState}>
                  <i className="bi bi-inbox"></i>
                  <p>Модели не найдены</p>
                  <span>Создайте первую модель</span>
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
            <th>Название</th>
            <th>Архитектура</th>
            <th>Версия</th>
            <th>Статус</th>
            <th>Размер</th>
            <th>Обновлена</th>
            <th>Действия</th>
          </tr>
        </thead>
        <tbody>
          {models.map(model => (
            <ModelRow 
              key={model.id}
              model={model}
              onEdit={onEdit}
              onActivate={onActivate}
              onDelete={onDelete}
              onDownload={onDownload}
            />
          ))}
        </tbody>
      </table>
    </div>
  )
}