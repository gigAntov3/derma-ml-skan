import { createContext, useContext, useState, useEffect } from 'react'
import { login as apiLogin, register as apiRegister, logout as apiLogout } from '../../features/auth/api/authApi'
import { getCurrentUser, updateCurrentUser } from '../../features/users/api/usersApi'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    const initAuth = async () => {
      const token = localStorage.getItem('access_token')
      if (token) {
        try {
          // Роли приходят с бэкенда!
          const userData = await getCurrentUser()
          setUser({
            id: userData.id,
            email: userData.email,
            firstName: userData.first_name,
            lastName: userData.last_name,
            middleName: userData.middle_name,
            phone: userData.phone,
            birthDate: userData.birth_date,
            roles: userData.roles, // <-- Роли с бэкенда
            isActive: userData.is_active,
            createdAt: userData.created_at,
          })
          localStorage.setItem('dermaclinic_user', JSON.stringify(userData))
        } catch (error) {
          console.error('Failed to get current user:', error)
          localStorage.removeItem('access_token')
          localStorage.removeItem('dermaclinic_user')
        }
      }
      setLoading(false)
    }

    initAuth()
  }, [])

  const login = async (email, password) => {
    setError(null)
    setLoading(true)
    
    try {
      const result = await apiLogin({ email, password })
      if (result.success) {
        // Получаем пользователя с ролями с бэкенда
        const userData = await getCurrentUser()
        const formattedUser = {
          id: userData.id,
          email: userData.email,
          firstName: userData.first_name,
          lastName: userData.last_name,
          middleName: userData.middle_name,
          phone: userData.phone,
          birthDate: userData.birth_date,
          roles: userData.roles, // <-- Роли с бэкенда
          isActive: userData.is_active,
          createdAt: userData.created_at,
        }
        setUser(formattedUser)
        localStorage.setItem('dermaclinic_user', JSON.stringify(userData))
        return { success: true, user: formattedUser }
      }
    } catch (err) {
      setError(err.message || 'Ошибка входа')
      return { success: false, error: err.message }
    } finally {
      setLoading(false)
    }
  }

  const register = async (userData) => {
    setError(null)
    setLoading(true)
    
    try {
      const result = await apiRegister(userData)
      if (result.success) {
        // После регистрации пользователь уже авторизован
        const userDataFromApi = await getCurrentUser()
        const formattedUser = {
          id: userDataFromApi.id,
          email: userDataFromApi.email,
          firstName: userDataFromApi.first_name,
          lastName: userDataFromApi.last_name,
          middleName: userDataFromApi.middle_name,
          phone: userDataFromApi.phone,
          birthDate: userDataFromApi.birth_date,
          roles: userDataFromApi.roles,
          isActive: userDataFromApi.is_active,
          createdAt: userDataFromApi.created_at,
        }
        setUser(formattedUser)
        localStorage.setItem('dermaclinic_user', JSON.stringify(userDataFromApi))
        return { success: true, user: formattedUser }
      }
    } catch (err) {
      setError(err.message || 'Ошибка регистрации')
      return { success: false, error: err.message }
    } finally {
      setLoading(false)
    }
  }

  const logout = async () => {
    await apiLogout()
    setUser(null)
    setError(null)
  }

  const updateUserProfile = async (updateData) => {
    try {
      // Обновляем на сервере
      await updateCurrentUser(updateData)
      
      // Получаем свежие данные
      const freshUserData = await getCurrentUser()
      
      // Форматируем в camelCase
      const formattedUser = {
        id: freshUserData.id,
        email: freshUserData.email,
        firstName: freshUserData.first_name,
        lastName: freshUserData.last_name,
        middleName: freshUserData.middle_name,
        phone: freshUserData.phone,
        birthDate: freshUserData.birth_date,
        roles: freshUserData.roles,
        isActive: freshUserData.is_active,
        createdAt: freshUserData.created_at,
      }
      
      // Обновляем состояние
      setUser(formattedUser)
      
      // Обновляем localStorage
      localStorage.setItem('dermaclinic_user', JSON.stringify(freshUserData))
      
      return { success: true, user: formattedUser }
    } catch (error) {
      console.error('Failed to update user:', error)
      return { success: false, error: error.message }
    }
  }

  const value = {
    user,
    loading,
    error,
    login,
    register,
    logout,
    updateUserProfile,
    isAuthenticated: !!user,
    isAdmin: user?.roles?.includes('admin') || false,
    isDoctor: user?.roles?.includes('doctor') || false,
    isPatient: user?.roles?.includes('patient') || false,
    isDev: user?.roles?.includes('dev') || false,
    userRoles: user?.roles || []
  }

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider')
  }
  return context
}