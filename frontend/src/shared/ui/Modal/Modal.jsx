import { useEffect } from 'react'
import { cn } from '../../lib/cn'
import styles from './Modal.module.css'

export default function Modal({ isOpen, onClose, title, children, size = 'medium' }) {
  useEffect(() => {
    const handleEsc = (e) => {
      if (e.key === 'Escape') onClose()
    }
    
    if (isOpen) {
      document.addEventListener('keydown', handleEsc)
      document.body.style.overflow = 'hidden'
    }
    
    return () => {
      document.removeEventListener('keydown', handleEsc)
      document.body.style.overflow = 'unset'
    }
  }, [isOpen, onClose])

  if (!isOpen) return null

  return (
    <div className={styles.overlay} onClick={onClose}>
      <div className={cn(styles.modal, size === 'large' && styles.modalLarge)} onClick={(e) => e.stopPropagation()}>
        <div className={styles.header}>
          <h4 className={styles.title}>
            <i className="bi bi-cpu" style={{ color: '#1f7a63' }}></i>
            {title}
          </h4>
          <button className={styles.closeBtn} onClick={onClose}>&times;</button>
        </div>
        <div className={styles.body}>
          {children}
        </div>
      </div>
    </div>
  )
}