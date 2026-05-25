export const initialPatients = [
  { 
    id: 1, 
    fullname: "Анна Смирнова", 
    email: "anna@example.com", 
    phone: "+7 (903) 123-45-67", 
    birthDate: "1990-05-15", 
    gender: "female", 
    registered: "2024-01-10" 
  },
  { 
    id: 2, 
    fullname: "Михаил Петров", 
    email: "mikhail@example.com", 
    phone: "+7 (903) 234-56-78", 
    birthDate: "1985-08-22", 
    gender: "male", 
    registered: "2024-01-15" 
  },
  { 
    id: 3, 
    fullname: "Елена Васильева", 
    email: "elena@example.com", 
    phone: "+7 (903) 345-67-89", 
    birthDate: "1995-12-03", 
    gender: "female", 
    registered: "2024-01-20" 
  },
  { 
    id: 4, 
    fullname: "Дмитрий Соколов", 
    email: "dmitry@example.com", 
    phone: "+7 (903) 456-78-90", 
    birthDate: "1988-07-19", 
    gender: "male", 
    registered: "2024-01-25" 
  },
  // Добавим еще одного пациента для демонстрации
  { 
    id: 5, 
    fullname: "Ольга Новикова", 
    email: "olga@example.com", 
    phone: "+7 (903) 567-89-01", 
    birthDate: "2000-03-10", 
    gender: "female", 
    registered: "2024-02-01" 
  }
]

export const initialDoctorPatients = {
  "doctor@dermaclinic.ru": [1, 2, 3, 5],
  "admin@dermaclinic.ru": [1, 2, 3, 4, 5]
}