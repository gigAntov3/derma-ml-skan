import { initialPatients, initialDoctorPatients } from '../../entities/patient/model/patients.mock'
import { initialDoctors, initialPatientDoctors } from '../../features/doctors/model/doctors.mock'
import { initialPredictionsHistory } from '../../features/predictions/model/predictions.mock'

export function initializeData() {
  // Инициализируем пациентов
  if (!localStorage.getItem('dermaclinic_patients')) {
    localStorage.setItem('dermaclinic_patients', JSON.stringify(initialPatients))
  }
  
  // Инициализируем врачей
  if (!localStorage.getItem('dermaclinic_doctors')) {
    localStorage.setItem('dermaclinic_doctors', JSON.stringify(initialDoctors))
  }
  
  // Инициализируем отношения врач-пациент
  if (!localStorage.getItem('dermaclinic_doctor_patients')) {
    localStorage.setItem('dermaclinic_doctor_patients', JSON.stringify(initialDoctorPatients))
  }
  
  // Инициализируем отношения пациент-врач
  if (!localStorage.getItem('dermaclinic_patient_doctors')) {
    localStorage.setItem('dermaclinic_patient_doctors', JSON.stringify(initialPatientDoctors))
  }

  if (!localStorage.getItem('dermaclinic_predictions')) {
    localStorage.setItem('dermaclinic_predictions', JSON.stringify(initialPredictionsHistory))
  }
  
  // Инициализируем пользователей для демо
  if (!localStorage.getItem('dermaclinic_users')) {
    const initialUsers = [
      {
        id: 1,
        firstName: "Анна",
        lastName: "Ковальчук",
        email: "anna@example.com",
        password: "123456",
        role: "patient",
        registered: "2024-01-10"
      }
    ]
    localStorage.setItem('dermaclinic_users', JSON.stringify(initialUsers))
  }
}