import { apiClient } from '../../../shared/api/client'

// Получить историю предсказаний текущего пациента
export async function getMyPredictionHistory(skip = 0, limit = 50) {
  try {
    const response = await apiClient.get(`/patients/me/history?skip=${skip}&limit=${limit}`)
    return response
  } catch (error) {
    throw error
  }
}

// Получить детали предсказания по ID
export async function getPredictionDetails(predictionId) {
  try {
    const history = await getMyPredictionHistory(0, 100)
    const prediction = history.predictions.find(p => p.id === parseInt(predictionId))
    if (!prediction) {
      throw new Error('Предсказание не найдено')
    }
    return prediction
  } catch (error) {
    throw error
  }
}

// Создать новое предсказание
export async function createPatientPrediction(imageFile) {
  const formData = new FormData()
  formData.append('file', imageFile)
  
  try {
    const token = localStorage.getItem('access_token')
    const response = await fetch(`${apiClient.baseURL}/patients/me/predict`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
      },
      body: formData,
      credentials: 'include',
    })
    
    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || 'Ошибка предсказания')
    }
    
    return await response.json()
  } catch (error) {
    throw error
  }
}

// Получить список врачей пациента
export async function getMyDoctors() {
  try {
    const response = await apiClient.get('/patients/doctors')
    return response
  } catch (error) {
    throw error
  }
}

// Удалить врача из списка (если есть такой эндпоинт)
export async function removeDoctor(doctorId) {
  try {
    const response = await apiClient.delete(`/patients/doctors/${doctorId}`)
    return response
  } catch (error) {
    throw error
  }
}

export async function getMyRecommendation() {
  try {
    const response = await apiClient.get('/patients/me/recommendation')
    console.log('Full response:', response)
    
    // Если response уже содержит данные (массив или объект)
    if (response) {
      // Если пришел массив, берем первый элемент
      if (Array.isArray(response) && response.length > 0) {
        console.log('Response is array, taking first element')
        return response[0]
      }
      // Если пришел объект с полем diagnosis
      if (response.diagnosis !== undefined) {
        console.log('Response is object with diagnosis')
        return response
      }
      // Если response обернут в data
      if (response.data) {
        if (Array.isArray(response.data) && response.data.length > 0) {
          return response.data[0]
        }
        if (response.data.diagnosis !== undefined) {
          return response.data
        }
      }
    }
    
    console.log('No diagnosis found')
    return null
  } catch (error) {
    console.error('getMyRecommendation error:', error)
    if (error.response?.status === 404) {
      return null
    }
    throw error
  }
}