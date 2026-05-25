import styles from './SearchInput.module.css'

export default function SearchInput({ value, onChange }) {
  return (
    <div className={styles.wrapper}>
      <i className="bi bi-search"></i>
      <input 
        type="text" 
        placeholder="Поиск по имени, email или роли..."
        value={value}
        onChange={(e) => onChange(e.target.value)}
      />
    </div>
  )
}