import UserRow from './UserRow'
import styles from './UsersTable.module.css'

export default function UsersTable({ users, onEditUser, onDeleteUser }) {
  if (users.length === 0) {
    return (
      <div className={styles.card}>
        <table className={styles.table}>
          <thead>
            <tr>
              <th>Пользователь</th>
              <th>Email</th>
              <th>Роли</th>
              <th>Статус</th>
              <th>Дата регистрации</th>
              <th>Действия</th>
            </tr>
          </thead>
          <tbody>
            <tr className={styles.emptyRow}>
              <td colSpan="6">
                <div className={styles.emptyState}>
                  <i className="bi bi-inbox"></i>
                  <p>Пользователи не найдены</p>
                  <span>Попробуйте изменить критерии поиска</span>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    )
  }

  return (
    <div className={styles.card}>
      <table className={styles.table}>
        <thead>
          <tr>
            <th>Пользователь</th>
            <th>Email</th>
            <th>Роли</th>
            <th>Статус</th>
            <th>Дата регистрации</th>
            <th>Действия</th>
          </tr>
        </thead>
        <tbody>
          {users.map(user => (
            <UserRow 
              key={user.id}
              user={user}
              onEdit={onEditUser}
              onDelete={onDeleteUser}
            />
          ))}
        </tbody>
      </table>
    </div>
  )
}