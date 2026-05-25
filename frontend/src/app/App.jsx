import { RouterProvider } from 'react-router-dom'
import { AuthProvider } from './context/AuthContext'
import { router } from './router/router'
import { initializeData } from '../shared/lib/initializeData'
import './styles/globals.css'

// Инициализируем данные при первом запуске
initializeData()

function App() {
  return (
    <AuthProvider>
      <RouterProvider router={router} />
    </AuthProvider>
  )
}

export default App