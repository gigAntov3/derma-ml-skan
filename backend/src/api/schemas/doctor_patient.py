from pydantic import BaseModel, EmailStr, Field


class AddPatientRequest(BaseModel):
    """Запрос на добавление пациента"""
    patient_email: EmailStr = Field(..., description="Email пациента")


class RemovePatientRequest(BaseModel):
    """Запрос на добавление пациента"""
    patient_id: int = Field(..., description="ID пациента")