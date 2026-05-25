import Toast from './Toast'

export default function ToastContainer({ toast, onHide }) {
  if (!toast.visible) return null
  
  return (
    <Toast 
      message={toast.message} 
      bgColor={toast.bgColor} 
      onHide={onHide}
    />
  )
}