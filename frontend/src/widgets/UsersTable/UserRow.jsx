import UserAvatar from '../../entities/user/ui/UserAvatar'
import RoleBadge from '../../entities/user/ui/RoleBadge'
import StatusBadge from '../../entities/user/ui/StatusBadge'
import styles from './UserRow.module.css'

export default function UserRow({ user, onEdit, onDelete }) {
  return (
    <tr className={user.blocked ? styles.blockedRow : ''}>
      <td>
        <div className={styles.userInfo}>
          <UserAvatar fullname={user.fullname} blocked={user.blocked} />
          <span className={user.blocked ? styles.blockedName : styles.userName}>
            {user.fullname}
          </span>
        </div>
      </td>
      <td>{user.email}</td>
      <td>
        <div className={styles.rolesContainer}>
          {user.roles.map(role => (
            <RoleBadge key={role} role={role} />
          ))}
        </div>
      </td>
      <td>
        <StatusBadge blocked={user.blocked} />
      </td>
      <td>{user.registered}</td>
      <td>
        <div className={styles.actions}>
          <i 
            className="bi bi-pencil-square" 
            onClick={() => onEdit(user.id)}
            title="Редактировать"
          />
          <i 
            className="bi bi-trash3" 
            onClick={() => onDelete(user.id)}
            title="Удалить"
          />
        </div>
      </td>
    </tr>
  )
}