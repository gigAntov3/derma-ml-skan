from fastapi import APIRouter, Depends, HTTPException, Query, status
from typing import List

from api.dependencies.doctor_patient import get_doctor_patient_service
from api.dependencies.auth import get_current_user_id
from api.decorators.roles import require_roles
from api.dependencies.medical import get_medical_service
from api.dependencies.predictions import get_prediction_service
from api.schemas.doctor_patient import AddPatientRequest
from api.schemas.medical import MedicalRecommendationResponse
from api.schemas.predictions import PredictionHistoryListResponse
from api.schemas.users import UserResponse
from services.doctor_patient import DoctorPatientService

from api.schemas.base import SuccessResponseSchema
from services.medical_service import MedicalService
from services.predictions import PredictionService


router = APIRouter(
    prefix="/patients",
    tags=["Patients"]
)


@router.get("/doctors", response_model=List[UserResponse])
@require_roles(['patient'])
async def get_my_doctors(
    current_user_id: int = Depends(get_current_user_id),
    service: DoctorPatientService = Depends(get_doctor_patient_service),
):
    """
    Получить список всех врачей пациента (только для пациентов)
    """
    return await service.get_patient_doctors(current_user_id)


@router.delete("/doctors/{doctor_id}", response_model=SuccessResponseSchema)
@require_roles(['patient'])
async def remove_doctor_from_patient(
    doctor_id: int,
    current_user_id: int = Depends(get_current_user_id),
    service: DoctorPatientService = Depends(get_doctor_patient_service),
):
    """
    Пациент отвязывается от врача (только для пациентов)
    """
    await service.remove_doctor(current_user_id, doctor_id)
    return SuccessResponseSchema(message=f"Doctor {doctor_id} removed from your list")


@router.get("/me/history", response_model=PredictionHistoryListResponse)
@require_roles(['patient'])
async def get_my_predictions_history(
    skip: int = Query(0, ge=0, description="Количество пропускаемых записей"),
    limit: int = Query(50, ge=1, le=100, description="Лимит записей"),
    service: PredictionService = Depends(get_prediction_service),
    current_user_id: int = Depends(get_current_user_id),
):
    """
    Пациент получает историю своих предсказаний
    Доступно только для роли 'patient'
    """
    return await service.get_patient_predictions_history(
        patient_id=current_user_id,
        current_user_id=current_user_id,
        skip=skip,
        limit=limit
    )


@router.get(
    "/me/recommendation",
    response_model=MedicalRecommendationResponse
)
async def get_patient_recommendation(
    current_user_id: int = Depends(get_current_user_id),
    service: MedicalService = Depends(get_medical_service)
) -> List[MedicalRecommendationResponse]:
    """
    Получает все рекомендации пациента.
    
    Доступ:
    - Сам пациент
    - Врач, который связан с пациентом
    - Администратор
    """
    return await service.get_recommendation(
        current_user_id=current_user_id
    )