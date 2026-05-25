from fastapi import HTTPException, status
from utils.database.uow import UnitOfWork
from api.schemas.users import UserResponse
from typing import List


class DoctorPatientService:
    """Сервис для управления связями врач-пациент"""
    
    def __init__(self, uow: UnitOfWork):
        self.uow = uow
    
    async def add_patient(self, doctor_id: int, patient_email: str) -> UserResponse:
        """
        Добавляет пациента врачу по email
        Вся бизнес-логика здесь
        """
        async with self.uow as uow:
            # 1. Проверяем существование врача
            doctor = await uow.users.get_by_id(doctor_id)
            if not doctor:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Doctor not found"
                )
            
            # 2. Проверяем роль врача
            doctor_roles = [role.code for role in doctor.roles]
            if "doctor" not in doctor_roles:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="User is not a doctor"
                )
            
            # 3. Находим пациента по email
            patient = await uow.users.get_by_email(patient_email)
            if not patient:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Patient not found"
                )
            
            # 4. Проверяем роль пациента
            patient_roles = [role.code for role in patient.roles]
            if "patient" not in patient_roles and "user" not in patient_roles:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="User is not a patient"
                )
            
            # 5. Проверяем, не связаны ли уже
            existing = await uow.doctor_patients.get_by_doctor_and_patient(
                doctor_id, patient.id
            )
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Patient already added to this doctor"
                )
            
            # 6. Создаем связь
            await uow.doctor_patients.create(doctor_id, patient.id)
            
            # 7. Коммит произойдет автоматически при выходе из контекста
        
        # Возвращаем данные пациента
        return UserResponse(
            id=patient.id,
            first_name=patient.first_name,
            last_name=patient.last_name,
            middle_name=patient.middle_name,
            email=patient.email,
            phone=patient.phone,
            birth_date=patient.birth_date,
            roles=patient_roles,
            is_active=patient.is_active,
            created_at=patient.created_at
        )
    
    async def get_my_patients(self, doctor_id: int) -> List[UserResponse]:
        """
        Получает список пациентов врача
        """
        async with self.uow as uow:
            # 1. Проверяем существование врача
            doctor = await uow.users.get_by_id(doctor_id)
            if not doctor:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Doctor not found"
                )
            
            # 2. Проверяем роль врача
            doctor_roles = [role.code for role in doctor.roles]
            if "doctor" not in doctor_roles:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="User is not a doctor"
                )
            
            # 3. Получаем пациентов
            patients = await uow.doctor_patients.get_patients_by_doctor(doctor_id)
        
        # Формируем ответ
        return [
            UserResponse(
                id=patient.id,
                first_name=patient.first_name,
                last_name=patient.last_name,
                middle_name=patient.middle_name,
                email=patient.email,
                phone=patient.phone,
                birth_date=patient.birth_date,
                roles=[role.code for role in patient.roles],
                is_active=patient.is_active,
                created_at=patient.created_at
            )
            for patient in patients
        ]
    
    async def get_patient(self, doctor_id: int, patient_id: int) -> UserResponse:
        """
        Получает пациента врача по ID
        """
        async with self.uow as uow:
            # 1. Проверяем существование врача
            doctor = await uow.users.get_by_id(doctor_id)
            if not doctor:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Doctor not found"
                )
            
            # 2. Проверяем роль врача
            doctor_roles = [role.code for role in doctor.roles]
            if "doctor" not in doctor_roles:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="User is not a doctor"
                )
            
            # 3. Получаем пациента
            patient = await uow.users.get_by_id(patient_id)
            if not patient:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Patient not found"
                )
            
            # 4. Проверяем роль пациента
            patient_roles = [role.code for role in patient.roles]
            if "patient" not in patient_roles and "user" not in patient_roles:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="User is not a patient"
                )
            
            # 5. Проверяем связь
            existing = await uow.doctor_patients.get_by_doctor_and_patient(
                doctor_id, patient_id
            )
            if not existing:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Patient is not associated with this doctor"
                )
        
        # Возвращаем данные пациента
        return UserResponse(
            id=patient.id,
            first_name=patient.first_name,
            last_name=patient.last_name,
            middle_name=patient.middle_name,
            email=patient.email,
            phone=patient.phone,
            birth_date=patient.birth_date,
            roles=patient_roles,
            is_active=patient.is_active,
            created_at=patient.created_at
        )
    
    async def remove_patient(self, doctor_id: int, patient_id: int) -> None:
        """
        Удаляет пациента от врача
        """
        async with self.uow as uow:
            # 1. Проверяем существование врача
            doctor = await uow.users.get_by_id(doctor_id)
            if not doctor:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Doctor not found"
                )
            
            # 2. Проверяем существование пациента
            patient = await uow.users.get_by_id(patient_id)
            if not patient:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Patient not found"
                )
            
            # 3. Проверяем, существует ли связь
            existing = await uow.doctor_patients.get_by_doctor_and_patient(
                doctor_id, patient_id
            )
            if not existing:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Patient is not associated with this doctor"
                )
            
            # 4. Удаляем связь
            await uow.doctor_patients.delete(doctor_id, patient_id)
    
    async def get_my_doctors(self, patient_id: int) -> List[UserResponse]:
        """
        Получает список врачей пациента
        """
        async with self.uow as uow:
            # Проверяем существование пациента
            patient = await uow.users.get_by_id(patient_id)
            if not patient:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Patient not found"
                )
            
            # Получаем врачей
            doctors = await uow.doctor_patients.get_doctors_by_patient(patient_id)
        
        return [
            UserResponse(
                id=doctor.id,
                first_name=doctor.first_name,
                last_name=doctor.last_name,
                middle_name=doctor.middle_name,
                email=doctor.email,
                phone=doctor.phone,
                birth_date=doctor.birth_date,
                roles=[role.code for role in doctor.roles],
                is_active=doctor.is_active,
                created_at=doctor.created_at
            )
            for doctor in doctors
        ]
    
    async def remove_doctor(self, patient_id: int, doctor_id: int) -> None:
        """
        Пациент отвязывается от врача
        """
        async with self.uow as uow:
            # 1. Проверяем существование пациента
            patient = await uow.users.get_by_id(patient_id)
            if not patient:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Patient not found"
                )
            
            # 2. Проверяем существование врача
            doctor = await uow.users.get_by_id(doctor_id)
            if not doctor:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Doctor not found"
                )
            
            # 3. Проверяем, существует ли связь
            existing = await uow.doctor_patients.get_by_doctor_and_patient(
                doctor_id, patient_id
            )
            if not existing:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Doctor is not associated with this patient"
                )
            
            # 4. Удаляем связь
            await uow.doctor_patients.delete(doctor_id, patient_id)
    
    async def get_patient_doctors(self, patient_id: int) -> List[UserResponse]:
        """
        Получает список всех врачей пациента
        """
        async with self.uow as uow:
            # Проверяем существование пациента
            patient = await uow.users.get_by_id(patient_id)
            if not patient:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Patient not found"
                )
            
            # Получаем врачей
            doctors = await uow.doctor_patients.get_doctors_by_patient(patient_id)
        
        return [
            UserResponse(
                id=doctor.id,
                first_name=doctor.first_name,
                last_name=doctor.last_name,
                middle_name=doctor.middle_name,
                email=doctor.email,
                phone=doctor.phone,
                birth_date=doctor.birth_date,
                roles=[role.code for role in doctor.roles],
                is_active=doctor.is_active,
                created_at=doctor.created_at
            )
            for doctor in doctors
        ]