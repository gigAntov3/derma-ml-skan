import { createBrowserRouter } from 'react-router-dom'
import LoginPage from '../../pages/LoginPage/LoginPage'
import RegisterPage from '../../pages/RegisterPage/RegisterPage'
import AdminUsersPage from '../../pages/AdminUsersPage/AdminUsersPage'
import DoctorPatientsPage from '../../pages/DoctorPatientsPage/DoctorPatientsPage'
import DoctorPatientDetailPage from '../../pages/DoctorPatientDetailPage/DoctorPatientDetailPage'
import DoctorAddAnalysisPage from '../../pages/DoctorAddAnalysisPage/DoctorAddAnalysisPage'
import PatientDoctorsPage from '../../pages/PatientDoctorsPage/PatientDoctorsPage'
import PatientHistoryPage from '../../pages/PatientHistoryPage/PatientHistoryPage'
import DevModelsPage from '../../pages/DevModelsPage/DevModelsPage'
import PatientAnalysisPage from '../../pages/PatientAnalysisPage/PatientAnalysisPage'
import PatientDashboardPage from '../../pages/PatientDashboardPage/PatientDashboardPage'
import ProtectedRoute from '../../shared/ui/ProtectedRoute/ProtectedRoute'


export const router = createBrowserRouter([
  {
    path: '/login',
    element: <LoginPage />
  },
  {
    path: '/register',
    element: <RegisterPage />
  },
  // Админские маршруты
  {
    path: '/admin/users',
    element: (
      <ProtectedRoute>
        <AdminUsersPage />
      </ProtectedRoute>
    )
  },
  // Врачебные маршруты
  {
    path: '/doctor/patients',
    element: (
      <ProtectedRoute>
        <DoctorPatientsPage />
      </ProtectedRoute>
    )
  },
  {
    path: '/doctor/patients/:id',
    element: (
      <ProtectedRoute>
        <DoctorPatientDetailPage />
      </ProtectedRoute>
    )
  },
  {
    path: '/doctor/patients/:id/analyse',
    element: (
      <ProtectedRoute>
        <DoctorAddAnalysisPage />
      </ProtectedRoute>
    )
  },
  // Пациентские маршруты
  {
    path: '/patient/analysis',
    element: (
      <ProtectedRoute>
        <PatientAnalysisPage />
      </ProtectedRoute>
    )
  },
  {
    path: '/patient/diagnosis',
    element: (
      <ProtectedRoute>
        <PatientDashboardPage />
      </ProtectedRoute>
    )
  },
  {
    path: '/patient/doctors',
    element: (
      <ProtectedRoute>
        <PatientDoctorsPage />
      </ProtectedRoute>
    )
  },
  {
    path: '/patient/history',
    element: (
      <ProtectedRoute>
        <PatientHistoryPage />
      </ProtectedRoute>
    )
  },
  // ML-разработка
  {
    path: '/dev/models',
    element: (
      <ProtectedRoute>
        <DevModelsPage />
      </ProtectedRoute>
    )
  },
  {
    path: '/',
    element: <LoginPage />
  },
  {
    path: '*',
    element: <LoginPage />
  }
])