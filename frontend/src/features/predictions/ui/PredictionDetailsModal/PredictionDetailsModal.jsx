import Modal from '../../../../shared/ui/Modal/Modal'
import Button from '../../../../shared/ui/Button/Button'
import AuthImage from '../../../../shared/ui/AuthImage/AuthImage'
import styles from './PredictionDetailsModal.module.css'

export default function PredictionDetailsModal({ isOpen, onClose, prediction }) {
  if (!prediction) return null

  const formatDate = (dateString) => {
    if (!dateString) return 'Дата неизвестна'
    const date = new Date(dateString)
    return date.toLocaleDateString('ru-RU', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  const malignantProbability = (prediction.malignant?.probability || 0) * 100
  const isMalignant = prediction.malignant?.detected || false
  const melanomaProbability = (prediction.melanoma?.probability || 0) * 100
  const hasMelanoma = prediction.melanoma?.detected || false

  const diagnoses = [
    { name: 'Меланома', value: prediction.diagnosis?.probabilities?.melanoma || 0, color: '#e0745f' },
    { name: 'Невус', value: prediction.diagnosis?.probabilities?.nevus || 0, color: '#1f7a63' },
    { name: 'Базалиома', value: prediction.diagnosis?.probabilities?.basal_cell_carcinoma || 0, color: '#ffc107' },
    { name: 'Актинический кератоз', value: prediction.diagnosis?.probabilities?.actinic_keratosis || 0, color: '#8aa79b' }
  ].sort((a, b) => b.value - a.value)

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="Результат анализа" size="large">
      <div className={styles.container}>
        {/* Изображения с использованием AuthImage для URL */}
        <div className={styles.imagesSection}>
          <div className={styles.imageCard}>
            <div className={styles.imageLabel}>
              <i className="bi bi-image"></i> Исследуемый участок
            </div>
            <AuthImage 
              src={prediction.image_url}
              alt="Original"
              className={styles.patientImage}
            />
          </div>
          <div className={styles.imageCard}>
            <div className={styles.imageLabel}>
              <i className="bi bi-thermometer-half"></i> Тепловая карта
            </div>
            <AuthImage 
              src={prediction.heatmap_url}
              alt="Heatmap"
              className={styles.heatmapImage}
            />
          </div>
        </div>

        {/* Информация о модели */}
        <div className={styles.modelCard}>
          <div className={styles.modelIcon}>
            <i className="bi bi-cpu"></i>
          </div>
          <div className={styles.modelInfo}>
            <div className={styles.modelName}>{prediction.model?.name || 'Неизвестная модель'}</div>
            <div className={styles.modelVersion}>Версия {prediction.model?.current_version?.version || '?'}</div>
          </div>
          <div className={styles.modelDate}>
            <i className="bi bi-calendar3"></i> {formatDate(prediction.created_at)}
          </div>
        </div>

        {/* Остальной код без изменений */}
        <div className={styles.probabilitiesMain}>
          <div className={styles.probabilityCard}>
            <div className={styles.probabilityCardHeader}>
              <i className={`bi ${isMalignant ? 'bi-exclamation-triangle-fill' : 'bi-shield-check'}`}></i>
              <span>Злокачественность</span>
            </div>
            <div className={styles.probabilityCardValue}>
              {malignantProbability.toFixed(1)}%
            </div>
            <div className={styles.probabilityCardBar}>
              <div 
                className={styles.probabilityCardFill}
                style={{ width: `${malignantProbability}%`, backgroundColor: isMalignant ? '#e0745f' : '#1f7a63' }}
              />
            </div>
            <div className={styles.probabilityCardStatus}>
              {isMalignant ? 'Обнаружена' : 'Не обнаружена'}
            </div>
          </div>

          <div className={styles.probabilityCard}>
            <div className={styles.probabilityCardHeader}>
              <i className="bi bi-bandaid"></i>
              <span>Меланома</span>
            </div>
            <div className={styles.probabilityCardValue}>
              {melanomaProbability.toFixed(1)}%
            </div>
            <div className={styles.probabilityCardBar}>
              <div 
                className={styles.probabilityCardFill}
                style={{ width: `${melanomaProbability}%`, backgroundColor: hasMelanoma ? '#e0745f' : '#1f7a63' }}
              />
            </div>
            <div className={styles.probabilityCardStatus}>
              {hasMelanoma ? 'Обнаружена' : 'Не обнаружена'}
            </div>
          </div>
        </div>

        <div className={styles.probabilitiesSection}>
          <h4 className={styles.sectionTitle}>
            <i className="bi bi-pie-chart"></i> Распределение вероятностей
          </h4>
          <div className={styles.probabilitiesList}>
            {diagnoses.map((diag, idx) => (
              <div key={idx} className={styles.probabilityItem}>
                <div className={styles.probabilityHeader}>
                  <span className={styles.probabilityName}>{diag.name}</span>
                  <span className={styles.probabilityPercent}>{(diag.value * 100).toFixed(1)}%</span>
                </div>
                <div className={styles.probabilityBar}>
                  <div 
                    className={styles.probabilityFill}
                    style={{ width: `${diag.value * 100}%`, backgroundColor: diag.color }}
                  />
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className={styles.actions}>
          <Button onClick={onClose}>
            Закрыть
          </Button>
        </div>
      </div>
    </Modal>
  )
}