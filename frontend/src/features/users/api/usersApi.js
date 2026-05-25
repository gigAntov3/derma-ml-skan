import { apiClient } from '../../../shared/api/client'

export async function getCurrentUser() {
  try {
    const response = await apiClient.get('/users/me')
    return response
  } catch (error) {
    throw error
  }
}

export async function updateCurrentUser(data) {
  try {
    const response = await apiClient.patch('/users/me', data)
    return response
  } catch (error) {
    throw error
  }
}

export async function getAllUsers(role = null, offset = 0, limit = 100) {
  try {
    let url = `/users?offset=${offset}&limit=${limit}`
    if (role) {
      url += `&role=${role}`
    }
    const response = await apiClient.get(url)
    return response
  } catch (error) {
    throw error
  }
}

export async function getUserById(userId) {
  try {
    const response = await apiClient.get(`/users/${userId}`)
    return response
  } catch (error) {
    throw error
  }
}

export async function updateUserByAdmin(userId, data) {
  try {
    const response = await apiClient.patch(`/users/${userId}`, data)
    return response
  } catch (error) {
    throw error
  }
}