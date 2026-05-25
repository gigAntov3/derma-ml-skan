import styles from './ModelsTable.module.css'

const formatFileSize = (bytes) => {
  if (!bytes) return 'Не указан'
  const sizes = ['Б', 'КБ', 'МБ', 'ГБ']
  const i = Math.floor(Math.log(bytes) / Math.log(1024))
  return `${(bytes / Math.pow(1024, i)).toFixed(1)} ${sizes[i]}`
}

const formatDate = (dateString) => {
  if (!dateString) return 'Нет данных'
  const date = new Date(dateString)
  return date.toLocaleDateString('ru-RU', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric'
  })
}

const getArchitectureLabel = (arch) => {
  const labels = {
    resnet50: 'ResNet50',
    efficientnet_b3: 'EfficientNet-B3',
    densenet121: 'DenseNet121'
  }
  return labels[arch] || arch
}

export default function ModelRow({ model, onEdit, onActivate, onDelete, onDownload }) {
  return (
    <tr>
      <td>
        <strong>{model.name}</strong>
      </td>
      <td>
        <span className={styles.architecture}>
          <i className="bi bi-cpu"></i>
          {getArchitectureLabel(model.architecture)}
        </span>
      </td>
      <td>
        <div className={styles.versionInfo}>
          <span className={styles.versionNumber}>v{model.current_version?.version || '1.0.0'}</span>
          {model.current_version?.created_at && (
            <span className={styles.versionDate}>
              {formatDate(model.current_version.created_at)}
            </span>
          )}
        </div>
      </td>
      <td>
        <span className={`${styles.statusBadge} ${model.is_active ? styles.statusActive : styles.statusInactive}`}>
          <i className={`bi ${model.is_active ? 'bi-check-circle-fill' : 'bi-circle'}`}></i>
          {model.is_active ? 'Активна' : 'Неактивна'}
        </span>
      </td>
      <td>
        <span className={styles.fileSize}>
          {formatFileSize(model.current_version?.file_size)}
        </span>
      </td>
      <td>
        <span className={styles.fileSize}>
          {formatDate(model.updated_at || model.created_at)}
        </span>
      </td>
      <td className={styles.actions}>
        <button
          className={styles.actionBtn}
          onClick={() => onEdit(model)}
          title="Редактировать"
        >
          <i className="bi bi-pencil"></i>
        </button>
        {!model.is_active && (
          <button
            className={`${styles.actionBtn} ${styles.activateBtn}`}
            onClick={() => onActivate(model.id)}
            title="Активировать"
          >
            <i className="bi bi-play-fill"></i>
          </button>
        )}
        <button
          className={`${styles.actionBtn} ${styles.downloadBtn}`}
          onClick={() => onDownload(model.id)}
          title="Скачать"
        >
          <i className="bi bi-download"></i>
        </button>
        <button
          className={`${styles.actionBtn} ${styles.deleteBtn}`}
          onClick={() => onDelete(model.id, model.name)}
          title="Удалить"
        >
          <i className="bi bi-trash"></i>
        </button>
      </td>
    </tr>
  )
}