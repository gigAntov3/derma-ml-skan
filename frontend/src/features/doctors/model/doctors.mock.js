export const initialDoctors = [
  { 
    id: 1, 
    fullname: "Алексей Воронов", 
    email: "alexey@dermaclinic.ru", 
    phone: "+7 (903) 111-22-33",
    birthDate: "1975-03-15",
    registered: "2024-01-10" 
  },
  { 
    id: 2, 
    fullname: "Мария Докторова", 
    email: "mdoctor@clinic.ru", 
    phone: "+7 (903) 444-55-66",
    birthDate: "1980-07-22",
    registered: "2024-01-15" 
  },
  { 
    id: 3, 
    fullname: "Екатерина Смирнова", 
    email: "ekaterina@dermaclinic.ru", 
    phone: "+7 (903) 777-88-99",
    birthDate: "1985-12-03",
    registered: "2024-01-20" 
  },
  { 
    id: 4, 
    fullname: "Дмитрий Админов", 
    email: "admin@dermaclinic.ru", 
    phone: "+7 (903) 000-11-22",
    birthDate: "1970-08-19",
    registered: "2024-01-25" 
  }
]

export const initialPatientDoctors = {
  "patient@dermaclinic.ru": [1, 2],
  "anna@example.com": [1],
  "mikhail@example.com": [2],
  "elena@example.com": [1, 3],
  "dmitry@example.com": [4],
  "olga@example.com": [2]
}