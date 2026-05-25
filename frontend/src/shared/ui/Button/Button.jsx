import { cn } from '../../lib/cn'
import styles from './Button.module.css'

export default function Button({ 
  children, 
  onClick, 
  type = 'button',
  variant = 'primary',
  loading = false,
  disabled = false,
  icon,
  className 
}) {
  return (
    <button
      type={type}
      onClick={onClick}
      disabled={disabled || loading}
      className={cn(styles.button, styles[variant], className)}
    >
      {loading && <i className="bi bi-hourglass-split"></i>}
      {!loading && icon && <i className={`bi ${icon}`}></i>}
      <span>{children}</span>
    </button>
  )
}