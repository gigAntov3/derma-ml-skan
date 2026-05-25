export const calculateAge = (birthDate) => {
    if (!birthDate) return 'Не указан'
    
    const today = new Date()
    const birth = new Date(birthDate)
    let age = today.getFullYear() - birth.getFullYear()
    const monthDiff = today.getMonth() - birth.getMonth()
    
    if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birth.getDate())) {
      age--
    }
    
    return `${age} ${getAgeWord(age)}`
  }
  
  const getAgeWord = (age) => {
    const lastDigit = age % 10
    const lastTwoDigits = age % 100
    
    if (lastTwoDigits >= 11 && lastTwoDigits <= 14) {
      return 'лет'
    }
    
    switch (lastDigit) {
      case 1:
        return 'год'
      case 2:
      case 3:
      case 4:
        return 'года'
      default:
        return 'лет'
    }
  }