import styles from './Select.module.css'

export default function Select({
  label,
  icon,
  value,
  onChange,
  options,
  error
}) {
  return (
    <div className={styles.group}>
      {label && (
        <label className={styles.label}>
          <i className={`bi ${icon}`}></i>
          <span>{label}</span>
        </label>
      )}
      <select
        value={value}
        onChange={onChange}
        className={`${styles.select} ${error ? styles.error : ''}`}
      >
        {options.map(option => (
          <option key={option.value} value={option.value}>
            {option.label}
          </option>
        ))}
      </select>
      {error && <span className={styles.errorMessage}>{error}</span>}
    </div>
  )
}