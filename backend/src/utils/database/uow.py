from typing import AsyncGenerator, Callable, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from .engine import session_factory
from repositories import (
    UserRepository,
    RoleRepository,
    SkinImageRepository,
    DoctorPatientRepository,
    MLModelRepository,
    ModelVersionRepository,
    PredictionRepository,
    HeatmapRepository,
    MedicalRecommendationRepository
)

class UnitOfWork():
    def __init__(self, session_factory: Callable[[], AsyncSession]):
        self._session_factory = session_factory
        self._session: Optional[AsyncSession] = None
        
    async def __aenter__(self):
        self._session = self._session_factory()

        await self._session.begin()
        
        self._users = UserRepository(self._session)
        self._roles = RoleRepository(self._session)
        self._skin_images = SkinImageRepository(self._session)
        self._doctor_patients = DoctorPatientRepository(self._session)
        self._ml_models = MLModelRepository(self._session)
        self._model_versions = ModelVersionRepository(self._session)
        self._predictions = PredictionRepository(self._session)
        self._heatmaps = HeatmapRepository(self._session)
        self._medical_recommendations = MedicalRecommendationRepository(self._session)
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            await self.rollback()
        else:
            await self.commit()
        await self._session.close()
    
    async def commit(self):
        await self._session.commit()
    
    async def rollback(self):
        await self._session.rollback()

    @property
    def users(self) -> UserRepository:
        return self._users

    @property
    def roles(self) -> RoleRepository:
        return self._roles

    @property
    def skin_images(self) -> SkinImageRepository:
        return self._skin_images
    
    @property
    def doctor_patients(self) -> DoctorPatientRepository:
        return self._doctor_patients
    

    @property
    def ml_models(self) -> MLModelRepository:
        return self._ml_models
    
    @property
    def model_versions(self) -> ModelVersionRepository:
        return self._model_versions
    
    @property
    def predictions(self) -> PredictionRepository:
        return self._predictions
    
    @property
    def heatmaps(self) -> HeatmapRepository:
        return self._heatmaps
    
    @property
    def medical_recommendations(self) -> MedicalRecommendationRepository:
        return self._medical_recommendations


async def get_unit_of_work() -> AsyncGenerator[UnitOfWork, None]:
    async with UnitOfWork(session_factory) as uow:
        yield uow