from fastapi import Depends
from services.doctor_patient import DoctorPatientService
from utils.database.uow import UnitOfWork, get_unit_of_work


async def get_doctor_patient_service(
    uow: UnitOfWork = Depends(get_unit_of_work),
) -> DoctorPatientService:
    return DoctorPatientService(uow=uow)