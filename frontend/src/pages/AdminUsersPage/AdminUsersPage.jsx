import { useState, useCallback, useMemo, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../../app/context/AuthContext'
import Sidebar from '../../widgets/Sidebar/Sidebar'
import UsersTable from '../../widgets/UsersTable/UsersTable'
import SearchInput from '../../features/search-users/SearchInput'
import RoleFilter from '../../features/filter-users/RoleFilter'
import EditUserModal from '../../features/edit-user/EditUserModal'
import PageHeader from '../../shared/ui/PageHeader/PageHeader'
import { useToast } from '../../shared/hooks/useToast'
import { useModal } from '../../shared/hooks/useModal'
import ToastContainer from '../../shared/ui/Toast/ToastContainer'
import { getAllUsers, updateUserByAdmin } from '../../features/users/api/usersApi'
import styles from './AdminUsersPage.module.css'

export default function AdminUsersPage() {
  const navigate = useNavigate()
  const { isAuthenticated, logout, user } = useAuth()
  const [users, setUsers] = useState([])
  const [loading, setLoading] = useState(true)
  const [searchTerm, setSearchTerm] = useState('')
  const [roleFilter, setRoleFilter] = useState('all')
  const [selectedUserId, setSelectedUserId] = useState(null)
  
  const { isOpen: isModalOpen, openModal: openEditModal, closeModal } = useModal()
  const { toast, showToast, hideToast } = useToast()

  useEffect(() => {
    if (!isAuthenticated) {
      navigate('/login')
      return
    }
    if (!user?.roles?.includes('admin')) {
      navigate('/doctor/patients')
      return
    }
    loadUsers()
  }, [isAuthenticated, navigate, user])

  const loadUsers = async () => {
    setLoading(true)
    try {
      const data = await getAllUsers()
      // Преобразуем данные из API в формат, понятный таблице
      const formattedUsers = data.map(user => ({
        id: user.id,
        fullname: `${user.last_name} ${user.first_name} ${user.middle_name || ''}`.trim(),
        email: user.email,
        roles: user.roles,
        registered: new Date(user.created_at).toISOString().split('T')[0],
        blocked: !user.is_active,
        phone: user.phone,
        birthDate: user.birth_date,
      }))
      setUsers(formattedUsers)
    } catch (error) {
      showToast('Ошибка загрузки пользователей', '#e0745f')
    } finally {
      setLoading(false)
    }
  }

  const handleEditUser = useCallback((userId) => {
    setSelectedUserId(userId)
    openEditModal()
  }, [openEditModal])

  const handleSaveUser = useCallback(async (updatedUser) => {
    try {
      // Подготавливаем данные для API
      const updateData = {
        first_name: updatedUser.fullname.split(' ')[0] || '',
        last_name: updatedUser.fullname.split(' ')[1] || '',
        middle_name: updatedUser.fullname.split(' ')[2] || '',
        email: updatedUser.email,
        is_active: !updatedUser.blocked,
        roles: updatedUser.roles,
      }
      
      await updateUserByAdmin(updatedUser.id, updateData)
      showToast('Данные обновлены', '#1f7a63')
      await loadUsers() // Перезагружаем список
      closeModal()
    } catch (error) {
      showToast('Ошибка обновления пользователя', '#e0745f')
    }
  }, [closeModal, showToast])

  const handleDeleteUser = useCallback(async (userId, userName) => {
    if (window.confirm(`Удалить пользователя "${userName}"? Это действие необратимо.`)) {
      try {
        // В API может не быть эндпоинта для удаления, используем деактивацию
        await updateUserByAdmin(userId, { is_active: false })
        showToast('Пользователь деактивирован', '#1f7a63')
        await loadUsers()
      } catch (error) {
        showToast('Ошибка удаления пользователя', '#e0745f')
      }
    }
  }, [showToast])

  // Фильтрация пользователей на клиенте (так как API может не поддерживать фильтрацию)
  const filteredUsers = useMemo(() => {
    let result = users
    
    if (searchTerm) {
      const term = searchTerm.toLowerCase()
      result = result.filter(user => 
        user.fullname.toLowerCase().includes(term) || 
        user.email.toLowerCase().includes(term) ||
        user.roles.some(role => role.toLowerCase().includes(term))
      )
    }
    
    if (roleFilter !== 'all') {
      result = result.filter(user => user.roles.includes(roleFilter))
    }
    
    return result
  }, [users, searchTerm, roleFilter])

  const selectedUser = useMemo(() => 
    users.find(user => user.id === selectedUserId), 
    [users, selectedUserId]
  )

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  if (loading) {
    return (
      <div className={styles.page}>
        <Sidebar onLogout={handleLogout} />
        <div className={styles.content}>
          <div className={styles.loading}>Загрузка пользователей...</div>
        </div>
      </div>
    )
  }

  return (
    <div className={styles.page}>
      <div className="bg-glow"></div>
      <div className="bg-dot-pattern"></div>
      
      <Sidebar onLogout={handleLogout} />
      
      <div className={styles.content}>
        <PageHeader 
          title="Управление пользователями"
          description="Каждому пользователю можно назначить несколько ролей и заблокировать доступ"
        />

        <div className={styles.searchFilterRow}>
          <SearchInput value={searchTerm} onChange={setSearchTerm} />
          <RoleFilter value={roleFilter} onChange={setRoleFilter} />
        </div>

        <UsersTable 
          users={filteredUsers} 
          onEditUser={handleEditUser}
          onDeleteUser={handleDeleteUser}
        />
      </div>

      {selectedUser && (
        <EditUserModal
          isOpen={isModalOpen}
          onClose={closeModal}
          user={selectedUser}
          onSave={handleSaveUser}
        />
      )}

      <ToastContainer toast={toast} onHide={hideToast} />
    </div>
  )
}