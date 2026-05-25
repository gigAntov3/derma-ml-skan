import styles from './UserAvatar.module.css'

export default function UserAvatar({ fullname, blocked }) {
  const initial = fullname.charAt(0).toUpperCase()
  
  return (
    <div className={`${styles.avatar} ${blocked ? styles.blocked : ''}`}>
      {initial}
    </div>
  )
}