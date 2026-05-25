export function validateLogin(email, password) {
    const errors = {}
    
    if (!email) {
      errors.email = 'Email обязателен'
    } else if (!/\S+@\S+\.\S+/.test(email)) {
      errors.email = 'Введите корректный email'
    }
    
    if (!password) {
      errors.password = 'Пароль обязателен'
    } else if (password.length < 4) {
      errors.password = 'Пароль должен содержать минимум 4 символа'
    }
    
    return errors
  }
  
  export function validateRegister(firstName, lastName, email, password) {
    const errors = {}
    
    if (!firstName) {
      errors.firstName = 'Имя обязательно'
    } else if (firstName.length < 2) {
      errors.firstName = 'Имя должно содержать минимум 2 символа'
    }
    
    if (!lastName) {
      errors.lastName = 'Фамилия обязательна'
    } else if (lastName.length < 2) {
      errors.lastName = 'Фамилия должна содержать минимум 2 символа'
    }
    
    if (!email) {
      errors.email = 'Email обязателен'
    } else if (!/\S+@\S+\.\S+/.test(email)) {
      errors.email = 'Введите корректный email'
    }
    
    if (!password) {
      errors.password = 'Пароль обязателен'
    } else if (password.length < 4) {
      errors.password = 'Пароль должен содержать минимум 4 символа'
    }
    
    return errors
  }