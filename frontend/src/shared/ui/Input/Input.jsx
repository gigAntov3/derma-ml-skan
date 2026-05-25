import { useState } from 'react'
import { cn } from '../../lib/cn'
import styles from './Input.module.css'

export default function Input({
  label,
  icon,
  type = 'text',
  placeholder,
  value,
  onChange,
  error,
  required
}) {
  const [showPassword, setShowPassword] = useState(false)
  const isPassword = type === 'password'
  const inputType = isPassword && showPassword ? 'text' : type

  return (
    <div className={styles.group}>
      {label && (
        <label className={styles.label}>
          <i className={`bi ${icon}`}></i>
          <span>{label}</span>
        </label>
      )}
      <div className={styles.inputWrapper}>
        <input
          type={inputType}
          placeholder={placeholder}
          value={value}
          onChange={onChange}
          className={cn(styles.input, error && styles.error)}
          required={required}
        />
        {isPassword && (
          <button
            type="button"
            onClick={() => setShowPassword(!showPassword)}
            className={styles.togglePassword}
          >
            <i className={`bi ${showPassword ? 'bi-eye-slash' : 'bi-eye'}`}></i>
          </button>
        )}
      </div>
      {error && <span className={styles.errorMessage}>{error}</span>}
    </div>
  )
}