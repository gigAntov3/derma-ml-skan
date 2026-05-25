from fastapi import APIRouter

from .auth import router as auth_router
from .users import router as users_router
from .skin_images import router as skin_images_router
from .doctors import router as doctors_router
from .patients import router as patients_router
from .ml_models import router as ml_models_router
from .predictions import router as predictions_router
from .heatmaps import router as heatmaps_router


router = APIRouter()

router.include_router(auth_router)
router.include_router(users_router)
router.include_router(skin_images_router)
router.include_router(doctors_router)
router.include_router(patients_router)
router.include_router(ml_models_router)
router.include_router(predictions_router)
router.include_router(heatmaps_router)