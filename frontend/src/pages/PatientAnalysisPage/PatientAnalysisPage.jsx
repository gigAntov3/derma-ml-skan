import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../../app/context/AuthContext'
import Sidebar from '../../widgets/Sidebar/Sidebar'
import PageHeader from '../../shared/ui/PageHeader/PageHeader'
import Button from '../../shared/ui/Button/Button'
import AuthImage from '../../shared/ui/AuthImage/AuthImage'
import { uploadSkinImage, createPrediction, getActiveModel } from '../../features/predictions/api/predictionsApi'
import { useToast } from '../../shared/hooks/useToast'
import ToastContainer from '../../shared/ui/Toast/ToastContainer'
import styles from './PatientAnalysisPage.module.css'

export default function PatientAnalysisPage() {
  const navigate = useNavigate()
  const { user, logout, isAuthenticated } = useAuth()
  const [selectedImage, setSelectedImage] = useState(null)
  const [previewUrl, setPreviewUrl] = useState(null)
  const [loading, setLoading] = useState(false)
  const [activeModel, setActiveModel] = useState(null)
  const [prediction, setPrediction] = useState(null)
  const [activeView, setActiveView] = useState('original')
  const [uploadedImageId, setUploadedImageId] = useState(null)
  const { toast, showToast, hideToast } = useToast()

  useEffect(() => {
    if (!isAuthenticated) {
      navigate('/login')
      return
    }
    loadActiveModel()
  }, [isAuthenticated, navigate])

  const loadActiveModel = async () => {
    try {
      const model = await getActiveModel()
      setActiveModel(model)
    } catch (error) {
      console.error(error)
    }
  }

  const handleImageSelect = (e) => {
    const file = e.target.files[0]
    if (file) {
      if (!file.type.startsWith('image/')) {
        showToast('Пожалуйста, выберите изображение', '#e0745f')
        return
      }
      if (file.size > 5 * 1024 * 1024) {
        showToast('Размер файла не должен превышать 5 МБ', '#e0745f')
        return
      }
      setSelectedImage(file)
      setPreviewUrl(URL.createObjectURL(file))
      setPrediction(null)
      setUploadedImageId(null)
    }
  }

  const handleAnalyze = async () => {
    if (!selectedImage) {
      showToast('Выберите изображение для анализа', '#e0745f')
      return
    }

    setLoading(true)
    try {
      // 1. Сначала загружаем изображение
      const uploadResult = await uploadSkinImage(selectedImage, user?.id)
      setUploadedImageId(uploadResult.id)
      
      // 2. Затем делаем предсказание
      const predictionResult = await createPrediction(user?.id, uploadResult.id)
      
      setPrediction(predictionResult)
      
      showToast('Анализ завершен успешно', '#1f7a63')
    } catch (error) {
      console.error('Analysis error:', error)
      showToast(error.message || 'Ошибка при анализе', '#e0745f')
    } finally {
      setLoading(false)
    }
  }

  const handleReset = () => {
    setSelectedImage(null)
    setPreviewUrl(null)
    setPrediction(null)
    setUploadedImageId(null)
  }

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  const formatPercent = (value) => ((value || 0) * 100).toFixed(1)

  const getDiagnosisLabel = (code) => {
    const labels = {
      melanoma: 'Меланома',
      nevus: 'Невус',
      basal_cell_carcinoma: 'Базалиома',
      actinic_keratosis: 'Актинический кератоз',
    }
    return labels[code] || 'Не определен'
  }

  const diagnosisLabel = getDiagnosisLabel(prediction?.diagnosis?.detected)
  const isMalignant = prediction?.malignant?.detected || false
  const malignantProb = formatPercent(prediction?.malignant?.probability)
  const melanomaProb = formatPercent(prediction?.melanoma?.probability)

  const allProbabilities = [
    { name: 'Меланома', value: prediction?.diagnosis?.probabilities?.melanoma || 0, color: '#e0745f' },
    { name: 'Невус', value: prediction?.diagnosis?.probabilities?.nevus || 0, color: '#1f7a63' },
    { name: 'Базалиома', value: prediction?.diagnosis?.probabilities?.basal_cell_carcinoma || 0, color: '#ffc107' },
    { name: 'Актинический кератоз', value: prediction?.diagnosis?.probabilities?.actinic_keratosis || 0, color: '#8aa79b' },
  ].sort((a, b) => b.value - a.value)

  return (
    <div className={styles.page}>
      <div className="bg-glow"></div>
      <div className="bg-dot-pattern"></div>

      <Sidebar onLogout={handleLogout} />

      <div className={styles.content}>
        <PageHeader 
          title="Анализ кожи"
          description="Загрузите фотографию — ИИ проанализирует её за секунды"
        />

        {!prediction && !loading && !previewUrl && (
          <div className={styles.uploadSection}>
            <div className={styles.floatingCircle1}></div>
            <div className={styles.floatingCircle2}></div>
            <div className={styles.floatingCircle3}></div>
            <div className={styles.floatingCircle4}></div>
            <div className={styles.medicalCross}>⚕️</div>
            <div className={styles.medicalCross2}>⚕️</div>

            <label className={styles.uploadCard}>
              <input type="file" accept="image/*" onChange={handleImageSelect} className={styles.fileInput} />
              <div className={styles.uploadContent}>
                <div className={styles.uploadIcon}>
                  <i className="bi bi-cloud-upload"></i>
                </div>
                <h3>Загрузите снимок</h3>
                <p>Нажмите или перетащите фото</p>
                <span>JPG, PNG до 5 МБ</span>
              </div>
            </label>
            
            {activeModel && (
              <div className={styles.modelBadge}>
                <i className="bi bi-cpu"></i>
                <span>{activeModel.name}</span>
                <span className={styles.version}>v{activeModel.current_version?.version}</span>
              </div>
            )}
          </div>
        )}

        {(previewUrl || loading || prediction) && (
          <div className={styles.analysisContainer}>
            {/* Левая часть — изображение */}
            <div className={styles.imagePanel}>
              <div className={styles.viewToggle}>
                <button 
                  className={`${styles.toggleBtn} ${activeView === 'original' ? styles.activeToggle : ''}`}
                  onClick={() => setActiveView('original')}
                >
                  <i className="bi bi-image"></i> Исходное
                </button>
                <button 
                  className={`${styles.toggleBtn} ${activeView === 'heatmap' ? styles.activeToggle : ''}`}
                  onClick={() => setActiveView('heatmap')}
                >
                  <i className="bi bi-thermometer-half"></i> Тепловая карта
                </button>
              </div>

              <div className={styles.imageArea}>
                {activeView === 'original' && (
                  <img src={previewUrl} alt="Original" className={styles.mainImage} />
                )}
                {activeView === 'heatmap' && (
                  <>
                    {prediction?.heatmap_url ? (
                      <AuthImage 
                        src={prediction.heatmap_url}
                        alt="Heatmap"
                        className={styles.mainImage}
                      />
                    ) : loading ? (
                      <div className={styles.imagePlaceholder}>
                        <i className="bi bi-hourglass-split"></i>
                        <span>Генерация тепловой карты...</span>
                      </div>
                    ) : (
                      <div className={styles.imagePlaceholder}>
                        <i className="bi bi-thermometer-half"></i>
                        <span>Начните анализ для получения тепловой карты</span>
                      </div>
                    )}
                  </>
                )}
              </div>
            </div>

            {/* Правая часть — результаты */}
            <div className={styles.resultsPanel}>
              {loading ? (
                <div className={styles.loadingState}>
                  <div className={styles.spinner}></div>
                  <p>Анализ изображения...</p>
                  <span>Загрузка изображения и обработка ИИ</span>
                </div>
              ) : prediction ? (
                <>
                  <div className={`${styles.metricItem} ${styles.diagnosisMetricItem}`}>
                    <div className={styles.metricLabel}>
                      <i className="bi bi-clipboard-heart"></i> Выявленный диагноз
                    </div>
                    <div className={`${styles.diagnosisValue} ${isMalignant ? styles.malignantText : styles.benignText}`}>
                      {diagnosisLabel}
                    </div>
                  </div>

                  <div className={styles.metricsRow}>
                    <div className={styles.metricItem}>
                      <div className={styles.metricLabel}>
                        <i className="bi bi-shield-shaded"></i> Злокачественность
                      </div>
                      <div className={styles.metricValue}>{malignantProb}%</div>
                      <div className={styles.metricBar}>
                        <div className={styles.metricFill} style={{ width: `${malignantProb}%`, backgroundColor: '#e0745f' }} />
                      </div>
                      <div className={styles.metricStatus}>
                        {isMalignant ? 'Обнаружена' : 'Не обнаружена'}
                      </div>
                    </div>

                    <div className={styles.metricItem}>
                      <div className={styles.metricLabel}>
                        <i className="bi bi-bandaid"></i> Меланома
                      </div>
                      <div className={styles.metricValue}>{melanomaProb}%</div>
                      <div className={styles.metricBar}>
                        <div className={styles.metricFill} style={{ width: `${melanomaProb}%`, backgroundColor: '#e0745f' }} />
                      </div>
                      <div className={styles.metricStatus}>
                        {parseFloat(melanomaProb) > 50 ? 'Высокий риск' : 'Низкий риск'}
                      </div>
                    </div>
                  </div>

                  <div className={styles.probabilitiesList}>
                    {allProbabilities.map((item, idx) => (
                      <div key={idx} className={styles.probabilityRow}>
                        <div className={styles.probabilityLabel}>
                          <span>{item.name}</span>
                          <span>{formatPercent(item.value)}%</span>
                        </div>
                        <div className={styles.probabilityTrack}>
                          <div
                            className={styles.probabilityProgress}
                            style={{ width: `${formatPercent(item.value)}%`, backgroundColor: item.color }}
                          />
                        </div>
                      </div>
                    ))}
                  </div>

                  <Button onClick={handleReset} variant="secondary" className={styles.newAnalysisBtn}>
                    <i className="bi bi-plus-lg"></i> Новый анализ
                  </Button>
                </>
              ) : (
                <div className={styles.readyState}>
                  <i className="bi bi-camera"></i>
                  <p>Нажмите для начала анализа</p>
                  <button onClick={handleAnalyze} className={styles.analyzeBtnCustom}>
                    <i className="bi bi-cpu"></i> Начать анализ
                  </button>
                </div>
              )}
            </div>
          </div>
        )}
      </div>

      <ToastContainer toast={toast} onHide={hideToast} />
    </div>
  )
}