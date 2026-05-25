import { ROLE_LABELS } from './role.constants'

export const getRoleName = (role) => ROLE_LABELS[role] || role

export const searchUsers = (users, searchTerm) => {
  const term = searchTerm.toLowerCase()
  return users.filter(user => 
    user.fullname.toLowerCase().includes(term) || 
    user.email.toLowerCase().includes(term) ||
    user.roles.some(role => getRoleName(role).toLowerCase().includes(term))
  )
}

export const filterUsers = (users, role) => {
  return users.filter(user => user.roles.includes(role))
}