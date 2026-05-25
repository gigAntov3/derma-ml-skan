import { useEffect } from 'react'
import styles from './Toast.module.css'

export default function Toast({ message, bgColor, icon, onHide }) {
  useEffect(() => {
    const timer = setTimeout(() => {
      onHide()
    }, 2200)
    
    return () => clearTimeout(timer)
  }, [onHide])

  return (
    <div className={styles.toast} style={{ backgroundColor: bgColor }}>
      <i className={`bi ${icon}`}></i>
      <span>{message}</span>
    </div>
  )
}