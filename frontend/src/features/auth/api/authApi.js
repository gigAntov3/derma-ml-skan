import { apiClient } from '../../../shared/api/client'

export async function login(credentials) {
  try {
    const response = await apiClient.post('/auth/login', credentials)
    
    // Сохраняем access token
    if (response.access_token) {
      localStorage.setItem('access_token', response.access_token)
    }
    
    return { success: true }
  } catch (error) {
    throw {
      success: false,
      message: error.message || 'Ошибка входа',
    }
  }
}

export async function register(userData) {
  try {
    const response = await apiClient.post('/auth/register', {
      first_name: userData.firstName,
      last_name: userData.lastName,
      email: userData.email,
      password: userData.password,
    })
    
    // Сохраняем access token
    if (response.access_token) {
      localStorage.setItem('access_token', response.access_token)
    }
    
    return { success: true }
  } catch (error) {
    throw {
      success: false,
      message: error.message || 'Ошибка регистрации',
    }
  }
}

export async function logout() {
  try {
    await apiClient.post('/auth/logout')
  } catch (error) {
    console.error('Logout error:', error)
  } finally {
    localStorage.removeItem('access_token')
    localStorage.removeItem('dermaclinic_user')
  }
}

export async function refreshToken() {
  try {
    const response = await apiClient.post('/auth/refresh')
    if (response.access_token) {
      localStorage.setItem('access_token', response.access_token)
    }
    return response
  } catch (error) {
    throw error
  }
}