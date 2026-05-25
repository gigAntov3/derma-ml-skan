export const useDeleteUser = (setUsers, showToast) => {
    const deleteUser = (userId) => {
      if (window.confirm('Удалить пользователя? Это действие необратимо.')) {
        setUsers(prev => prev.filter(user => user.id !== userId))
        showToast('Пользователь удален', '#c23d3d')
      }
    }
  
    return { deleteUser }
  }