import { apiClient } from '../../../shared/api/client'

// Загрузить изображение кожи
export async function uploadSkinImage(file, patientId = null) {
  const formData = new FormData()
  formData.append('file', file)
  if (patientId) {
    formData.append('patient_id', patientId.toString())
  }
  
  try {
    const token = localStorage.getItem('access_token')
    const response = await fetch(`${apiClient.baseURL}/skin-images/upload`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
      },
      body: formData,
      credentials: 'include',
    })
    
    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || 'Ошибка загрузки изображения')
    }
    
    return await response.json()
  } catch (error) {
    throw error
  }
}

// Получить изображение по ID
export async function getSkinImage(imageId) {
  try {
    const token = localStorage.getItem('access_token')
    const response = await fetch(`${apiClient.baseURL}/skin-images/${imageId}`, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`,
      },
      credentials: 'include',
    })
    
    if (!response.ok) {
      throw new Error('Ошибка получения изображения')
    }
    
    const blob = await response.blob()
    return URL.createObjectURL(blob)
  } catch (error) {
    throw error
  }
}

// Создать предсказание
export async function createPrediction(patientId, imageId, modelId = null) {
  try {
    const body = {
      pacient_id: patientId,
      image_id: imageId,
    }
    if (modelId) {
      body.model_id = modelId
    }
    
    const response = await apiClient.post('/predict', body)
    return response
  } catch (error) {
    throw error
  }
}

// Получить активную модель
export async function getActiveModel() {
  try {
    const response = await apiClient.get('/ml-models/active')
    return response
  } catch (error) {
    throw error
  }
}