import { API_BASE_URL, REQUEST_TIMEOUT } from './config'

class ApiClient {
  constructor() {
    this.baseURL = API_BASE_URL
    this.timeout = REQUEST_TIMEOUT
  }

  async request(endpoint, options = {}) {
    const url = `${this.baseURL}${endpoint}`
    
    const controller = new AbortController()
    const timeoutId = setTimeout(() => controller.abort(), this.timeout)

    try {
      const token = localStorage.getItem('access_token')
      
      const headers = {
        'Content-Type': 'application/json',
        ...options.headers,
      }

      if (token) {
        headers['Authorization'] = `Bearer ${token}`
      }

      const response = await fetch(url, {
        ...options,
        headers,
        signal: controller.signal,
        credentials: 'include', // Важно для отправки cookies
      })

      clearTimeout(timeoutId)

      // Если 401 - пытаемся обновить через refresh cookie
      if (response.status === 401) {
        // Пытаемся обновить access token через refresh cookie
        const refreshed = await this.refreshToken()
        
        if (refreshed) {
          // Получаем новый токен и повторяем запрос
          const newToken = localStorage.getItem('access_token')
          const newHeaders = {
            'Content-Type': 'application/json',
            ...options.headers,
            'Authorization': `Bearer ${newToken}`,
          }
          
          // Убираем старый Authorization если был
          if (options.headers) {
            delete options.headers.Authorization
          }
          
          // Повторяем запрос
          const retryResponse = await fetch(url, {
            ...options,
            headers: newHeaders,
            signal: controller.signal,
            credentials: 'include',
          })
          
          if (!retryResponse.ok) {
            throw new Error(`Request failed with status ${retryResponse.status}`)
          }
          
          const retryData = await retryResponse.json()
          return retryData
        } else {
          // Не удалось обновить - редирект на логин
          localStorage.removeItem('access_token')
          localStorage.removeItem('dermaclinic_user')
          window.location.href = '/login'
          throw new Error('Session expired')
        }
      }

      const data = await response.json()

      if (!response.ok) {
        throw {
          status: response.status,
          message: data.detail || data.message || 'Request failed',
          data,
        }
      }

      return data
    } catch (error) {
      clearTimeout(timeoutId)
      if (error.name === 'AbortError') {
        throw { message: 'Request timeout' }
      }
      throw error
    }
  }

  async refreshToken() {
    try {
      // Отправляем запрос на обновление - refresh token в cookies отправится автоматически
      const response = await fetch(`${this.baseURL}/auth/refresh`, {
        method: 'POST',
        credentials: 'include', // Важно: отправляет httpOnly cookie
        headers: {
          'Content-Type': 'application/json',
        },
      })

      if (response.ok) {
        const data = await response.json()
        // Сохраняем новый access token
        if (data.access_token) {
          localStorage.setItem('access_token', data.access_token)
          return true
        }
      }
      
      // Если refresh token истек или невалиден
      if (response.status === 401) {
        console.log('Refresh token expired or invalid')
        return false
      }
      
      return false
    } catch (error) {
      console.error('Token refresh failed:', error)
      return false
    }
  }

  get(endpoint, options = {}) {
    return this.request(endpoint, { ...options, method: 'GET' })
  }

  post(endpoint, body, options = {}) {
    return this.request(endpoint, {
      ...options,
      method: 'POST',
      body: JSON.stringify(body),
    })
  }

  put(endpoint, body, options = {}) {
    return this.request(endpoint, {
      ...options,
      method: 'PUT',
      body: JSON.stringify(body),
    })
  }

  patch(endpoint, body, options = {}) {
    return this.request(endpoint, {
      ...options,
      method: 'PATCH',
      body: JSON.stringify(body),
    })
  }

  delete(endpoint, options = {}) {
    return this.request(endpoint, { ...options, method: 'DELETE' })
  }
}

export const apiClient = new ApiClient()