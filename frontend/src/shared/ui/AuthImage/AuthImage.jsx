import { useState, useEffect } from 'react'
import { apiClient } from '../../api/client'
import styles from './AuthImage.module.css'

export default function AuthImage({ src, alt, className, onLoad, onError }) {
  const [imageUrl, setImageUrl] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    if (!src) {
      setError('Нет URL изображения')
      setLoading(false)
      return
    }

    // Если src уже полный URL, используем его
    if (src.startsWith('http://') || src.startsWith('https://')) {
      // Проверяем, не содержит ли URL localhost (тогда через прокси)
      if (src.includes('localhost') || src.includes('127.0.0.1')) {
        // Для локального API загружаем через fetch с токеном
        const fetchImage = async () => {
          setLoading(true)
          try {
            const token = localStorage.getItem('access_token')
            const response = await fetch(src, {
              headers: {
                'Authorization': `Bearer ${token}`,
              },
              credentials: 'include',
            })
            
            if (!response.ok) {
              throw new Error('Ошибка загрузки')
            }
            
            const blob = await response.blob()
            const url = URL.createObjectURL(blob)
            setImageUrl(url)
          } catch (err) {
            setError(err.message)
          } finally {
            setLoading(false)
          }
        }
        fetchImage()
      } else {
        // Внешние URL используем напрямую
        setImageUrl(src)
        setLoading(false)
      }
      return
    }

    // Относительный путь - загружаем через API
    const fetchImage = async () => {
      setLoading(true)
      setError(null)
      
      try {
        const token = localStorage.getItem('access_token')
        const fullUrl = src.startsWith('/') ? src : `/${src}`
        const response = await fetch(`${apiClient.baseURL}${fullUrl}`, {
          headers: {
            'Authorization': `Bearer ${token}`,
          },
          credentials: 'include',
        })

        if (!response.ok) {
          throw new Error(`Ошибка загрузки: ${response.status}`)
        }

        const blob = await response.blob()
        const url = URL.createObjectURL(blob)
        setImageUrl(url)
        
        if (onLoad) onLoad()
      } catch (err) {
        console.error('Error loading image:', err)
        setError(err.message)
        if (onError) onError(err)
      } finally {
        setLoading(false)
      }
    }

    fetchImage()

    return () => {
      if (imageUrl && !imageUrl.startsWith('http')) {
        URL.revokeObjectURL(imageUrl)
      }
    }
  }, [src])

  if (loading) {
    return (
      <div className={`${styles.placeholder} ${className || ''}`}>
        <i className="bi bi-hourglass-split"></i>
        <span>Загрузка...</span>
      </div>
    )
  }

  if (error || !imageUrl) {
    return (
      <div className={`${styles.placeholder} ${styles.error} ${className || ''}`}>
        <i className="bi bi-image"></i>
        <span>Изображение недоступно</span>
      </div>
    )
  }

  return <img src={imageUrl} alt={alt} className={className} />
}