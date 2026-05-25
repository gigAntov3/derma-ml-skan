import { apiClient } from '../../../shared/api/client'

// Получить список пациентов врача
export async function getDoctorPatients() {
  try {
    const response = await apiClient.get('/doctors/patients')
    return response
  } catch (error) {
    throw error
  }
}

// Получить данные пациента по ID
export async function getPatientById(patientId) {
  try {
    const response = await apiClient.get(`/doctors/patients/${patientId}`)
    return response
  } catch (error) {
    throw error
  }
}

// Добавить пациента по email
export async function addPatientToDoctor(patientEmail) {
  try {
    const response = await apiClient.post('/doctors/patients', { patient_email: patientEmail })
    return response
  } catch (error) {
    throw error
  }
}

// Удалить пациента
export async function removePatientFromDoctor(patientId) {
  try {
    const response = await apiClient.delete(`/doctors/patients/${patientId}`)
    return response
  } catch (error) {
    throw error
  }
}

// Получить историю предсказаний пациента (для врача)
export async function getPatientPredictionsForDoctor(patientId, skip = 0, limit = 50) {
  try {
    const response = await apiClient.get(`/doctors/patients/${patientId}/history?skip=${skip}&limit=${limit}`)
    return response
  } catch (error) {
    throw error
  }
}

// Получить рекомендации пациента
// Получить рекомендации пациента
export async function getPatientRecommendation(patientId) {
  try {
    const response = await apiClient.get(`/doctors/patients/${patientId}/recommendation`)
    console.log('Full response:', response)
    
    // apiClient уже вернул данные, поэтому response - это уже данные, а не axios response
    // Проверяем, что вернул apiClient
    if (response && typeof response === 'object') {
      // Если response имеет поля diagnosis или recommendations
      if ('diagnosis' in response || 'recommendations' in response) {
        console.log('Found diagnosis in response:', response)
        return response
      }
      // Если response обернут в data
      if (response.data && ('diagnosis' in response.data || 'recommendations' in response.data)) {
        console.log('Found diagnosis in response.data:', response.data)
        return response.data
      }
      // Если response - это массив
      if (Array.isArray(response) && response.length > 0) {
        console.log('Response is array:', response)
        return response[0]
      }
    }
    
    console.log('No valid data found, response structure:', response)
    return null
  } catch (error) {
    console.error('API getPatientRecommendation error:', error)
    if (error.response?.status === 404) {
      return null
    }
    throw error
  }
}

// Обновить рекомендации пациента
export async function updatePatientRecommendation(patientId, data) {
  try {
    const response = await apiClient.patch(`/doctors/patients/${patientId}/recommendation`, data)
    console.log('Update response:', response)
    return response
  } catch (error) {
    console.error('API updatePatientRecommendation error:', error)
    throw error
  }
}