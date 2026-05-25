from fastapi import APIRouter, Depends, HTTPException, Query, status
from typing import List

from api.dependencies.doctor_patient import get_doctor_patient_service
from api.dependencies.auth import get_current_user_id
from api.decorators.roles import require_roles
from api.dependencies.medical import get_medical_service
from api.dependencies.predictions import get_prediction_service
from api.schemas.doctor_patient import AddPatientRequest
from api.schemas.medical import MedicalRecommendationResponse, MedicalRecommendationUpdate
from api.schemas.predictions import PredictionHistoryListResponse
from api.schemas.users import UserResponse
from services.doctor_patient import DoctorPatientService

from api.schemas.base import SuccessResponseSchema
from services.medical_service import MedicalService
from services.predictions import PredictionService


router = APIRouter(
    prefix="/doctors",
    tags=["Doctors"]
)


@router.get("/patients", response_model=List[UserResponse])
@require_roles(['doctor'])
async def get_my_patients(
    current_user_id: int = Depends(get_current_user_id),
    service: DoctorPatientService = Depends(get_doctor_patient_service),
):
    """
    Получить список всех пациентов врача
    """
    return await service.get_my_patients(current_user_id)


@router.post("/patients", response_model=UserResponse)
@require_roles(['doctor'])
async def add_patient(
    request: AddPatientRequest,
    current_user_id: int = Depends(get_current_user_id),
    service: DoctorPatientService = Depends(get_doctor_patient_service),
):
    """
    Добавить пациента врачу по email (только для врачей)
    """
    return await service.add_patient(current_user_id, request.patient_email)


@router.get("/patients/{patient_id}", response_model=UserResponse)
@require_roles(['doctor'])
async def get_patient(
    patient_id: int,
    current_user_id: int = Depends(get_current_user_id),
    service: DoctorPatientService = Depends(get_doctor_patient_service),
):
    """
    Получить пациента по ID (только для врачей)
    """
    return await service.get_patient(current_user_id, patient_id)


@router.delete("/patients/{patient_id}")
@require_roles(['doctor'])
async def remove_patient(
    patient_id: int,
    current_user_id: int = Depends(get_current_user_id),
    service: DoctorPatientService = Depends(get_doctor_patient_service),
) -> SuccessResponseSchema:
    """
    Удалить пациента от врача (только для врачей)
    """
    await service.remove_patient(current_user_id, patient_id)
    return SuccessResponseSchema(message="Patient removed")


@router.get("/patients/{patient_id}/history", response_model=PredictionHistoryListResponse)
@require_roles(['doctor'])
async def get_patient_predictions_for_doctor(
    patient_id: int,
    skip: int = Query(0, ge=0, description="Количество пропускаемых записей"),
    limit: int = Query(50, ge=1, le=100, description="Лимит записей"),
    service: PredictionService = Depends(get_prediction_service),
    current_user_id: int = Depends(get_current_user_id),
):
    """
    Врач получает историю предсказаний своего пациента
    Доступно только для роли 'doctor'
    """
    return await service.get_patient_predictions_for_doctor(
        doctor_id=current_user_id,
        patient_id=patient_id,
        skip=skip,
        limit=limit
    )


@router.get(
    "/patients/{patient_id}/recommendation",
    response_model=MedicalRecommendationResponse
)
@require_roles(['doctor'])
async def get_patient_recommendation(
    patient_id: int,
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
    return await service.get_patient_recommendation(
        patient_id=patient_id,
        current_user_id=current_user_id
    )


@router.patch(
    "/patients/{patient_id}/recommendation",
    response_model=MedicalRecommendationResponse
)
@require_roles(['doctor'])
async def update_recommendation(
    patient_id: int,
    update_data: MedicalRecommendationUpdate,
    current_user_id: int = Depends(get_current_user_id),
    service: MedicalService = Depends(get_medical_service)
) -> MedicalRecommendationResponse:
    """
    Обновляет диагноз и рекомендации.
    
    Доступ: только для врача, который создал рекомендацию, или администратора.
    """
    return await service.update_recommendation(
        patient_id=patient_id,
        doctor_id=current_user_id,
        update_data=update_data
    )