import { apiClient } from '../../../shared/api/client'

// Получить список всех моделей
export async function getModels(skip = 0, limit = 100, onlyActive = false) {
  try {
    let url = `/ml-models?skip=${skip}&limit=${limit}`
    if (onlyActive) {
      url += `&only_active=true`
    }
    const response = await apiClient.get(url)
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

// Получить модель по ID
export async function getModelById(modelId) {
  try {
    const response = await apiClient.get(`/ml-models/${modelId}`)
    return response
  } catch (error) {
    throw error
  }
}

// Создать новую модель
export async function createModel(formData) {
  try {
    const formDataToSend = new FormData()
    formDataToSend.append('name', formData.name)
    formDataToSend.append('architecture', formData.architecture)
    if (formData.file) {
      formDataToSend.append('file', formData.file)
    }
    
    const token = localStorage.getItem('access_token')
    const response = await fetch(`${apiClient.baseURL}/ml-models`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
      },
      body: formDataToSend,
      credentials: 'include',
    })
    
    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || 'Ошибка создания модели')
    }
    
    return await response.json()
  } catch (error) {
    throw error
  }
}

// Обновить модель (имя, статус, добавить версию)
export async function updateModel(modelId, updateData, file = null) {
  try {
    const formDataToSend = new FormData()
    if (updateData.name) {
      formDataToSend.append('name', updateData.name)
    }
    if (updateData.is_active !== undefined) {
      formDataToSend.append('is_active', updateData.is_active.toString())
    }
    if (file) {
      formDataToSend.append('file', file)
    }
    
    const token = localStorage.getItem('access_token')
    const response = await fetch(`${apiClient.baseURL}/ml-models/${modelId}`, {
      method: 'PATCH',
      headers: {
        'Authorization': `Bearer ${token}`,
      },
      body: formDataToSend,
      credentials: 'include',
    })
    
    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || 'Ошибка обновления модели')
    }
    
    return await response.json()
  } catch (error) {
    throw error
  }
}

// Активировать модель (устанавливает is_active=true и деактивирует остальные)
export async function activateModel(modelId) {
  try {
    return await updateModel(modelId, { is_active: true })
  } catch (error) {
    throw error
  }
}

// Скачать файл модели
export async function downloadModel(modelId) {
  try {
    const token = localStorage.getItem('access_token')
    const response = await fetch(`${apiClient.baseURL}/ml-models/${modelId}/download`, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`,
      },
      credentials: 'include',
    })
    
    if (!response.ok) {
      throw new Error('Ошибка скачивания')
    }
    
    // Получаем имя файла из заголовка Content-Disposition
    const contentDisposition = response.headers.get('Content-Disposition')
    let filename = `model_${modelId}.pt`
    if (contentDisposition) {
      const match = contentDisposition.match(/filename=(.+)/)
      if (match) {
        filename = match[1]
      }
    }
    
    const blob = await response.blob()
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = filename
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    window.URL.revokeObjectURL(url)
    
    return { success: true }
  } catch (error) {
    throw error
  }
}

// Удалить модель
export async function deleteModel(modelId) {
  try {
    const response = await apiClient.delete(`/ml-models/${modelId}`)
    return response
  } catch (error) {
    throw error
  }
}

// Добавить новую версию модели (через update с файлом)
export async function addModelVersion(modelId, file) {
  try {
    return await updateModel(modelId, {}, file)
  } catch (error) {
    throw error
  }
}