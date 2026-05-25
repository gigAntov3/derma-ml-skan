import { useState, useCallback } from 'react'

export const useToast = () => {
  const [toast, setToast] = useState({ visible: false, message: '', bgColor: '#1f7a63', icon: 'bi-check-circle' })

  const showToast = useCallback((message, bgColor = '#1f7a63', icon = 'bi-check-circle') => {
    setToast({ visible: true, message, bgColor, icon })
  }, [])

  const hideToast = useCallback(() => {
    setToast(prev => ({ ...prev, visible: false }))
  }, [])

  return { toast, showToast, hideToast }
}