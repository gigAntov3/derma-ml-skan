import torch
import matplotlib.pyplot as plt
from matplotlib import cm
import torch.nn.functional as F
from pathlib import Path
from typing import Optional, Tuple, Dict, Any, List
from fastapi import HTTPException
import time
from PIL import Image
import cv2
import numpy as np

from models.predictions import Prediction
from services.ml_models import ModelService
from utils.database.uow import UnitOfWork
from models.ml_models import ModelVersion, MLModel
from models.skin_images import SkinImage
from models.heatmaps import PredictionHeatmap
from api.schemas.predictions import (
    PredictionResponse, MalignantInfo, MelanomaInfo,
    DiagnosisInfo, DiagnosisProbabilities, DiagnosisCode,
    PredictionRequest, PredictionHistoryListResponse
)
from api.schemas.ml_models import ModelResponseSchema, ModelVersionResponseSchema
from utils.ml_models.preprocessing import ImagePreprocessor
from utils.ml_models.model_loader import ModelLoader

from services.heatmaps import HeatmapService

from config import settings


class PredictionService:
    def __init__(self, uow: UnitOfWork, model_service: ModelService, heatmap_service: HeatmapService):
        self.uow = uow
        self.model_service = model_service
        self.heatmap_service = heatmap_service
        self.preprocessor = ImagePreprocessor(target_size=(224, 224), normalize=True)
        
        cache_size = getattr(settings, 'MODEL_CACHE_SIZE', 5)
        self.model_loader = ModelLoader(
            device=getattr(settings, 'MODEL_DEVICE', None),
            cache_size=cache_size
        )
        
        self.class_names = [
            DiagnosisCode.MELANOMA,
            DiagnosisCode.NEVUS,
            DiagnosisCode.BASAL_CELL_CARCINOMA,
            DiagnosisCode.ACTINIC_KERATOSIS
        ]
    
    async def predict(
        self,
        current_user_id: int,
        pacient_id: int,
        image_id: int,
        model_id: Optional[int] = None,
        generate_heatmap: bool = True
    ) -> PredictionResponse:
        """
        Выполнение предсказания с сохранением в БД
        """
        async with self.uow as uow:
            # Проверка доступа
            if current_user_id != pacient_id:
                doctor_patient = await uow.doctor_patients.get_by_doctor_and_patient(
                    current_user_id, pacient_id
                )
                if not doctor_patient:
                    raise HTTPException(
                        status_code=403,
                        detail=f"Patient {pacient_id} does not have access to image {image_id}"
                    )

            start_time = time.time()
            
            # 1. Получаем модель и последнюю версию
            model_from_db, model_version = await self._get_model_and_version(uow, model_id)
            
            # 2. Получаем путь к изображению и проверяем доступ
            image_path = await self._get_image_path_from_db(uow, image_id, pacient_id)
            
            if not Path(image_path).exists():
                raise HTTPException(
                    status_code=404,
                    detail=f"Image file not found at path: {image_path}"
                )
            
            # 3. Загружаем модель
            model = await self._load_model(model_version, model_from_db)
            
            # 4. Предобработка
            try:
                input_tensor = self.preprocessor.preprocess(image_path)
                input_tensor = input_tensor.to(next(model.parameters()).device)
            except Exception as e:
                raise HTTPException(
                    status_code=400,
                    detail=f"Failed to process image: {str(e)}"
                )
            
            # 5. Инференс
            with torch.no_grad():
                malignant_logits, melanoma_logits, class4_logits = model(input_tensor)
                
                malignant_prob = torch.sigmoid(malignant_logits).item()
                melanoma_prob = torch.sigmoid(melanoma_logits).item()
                
                class4_probs = F.softmax(class4_logits, dim=1).squeeze().cpu().numpy()
                if class4_probs.ndim == 2:
                    class4_probs = class4_probs[0]
            
            # Маппинг классов
            class_names = [
                DiagnosisCode.MELANOMA,
                DiagnosisCode.NEVUS,
                DiagnosisCode.BASAL_CELL_CARCINOMA,
                DiagnosisCode.ACTINIC_KERATOSIS
            ]
            
            predicted_idx = int(class4_probs.argmax())
            predicted_code = class_names[predicted_idx]
            
            prediction_time = (time.time() - start_time) * 1000
            
            # 6. Сохраняем предсказание в БД
            prediction_data = {
                'patient_id': pacient_id,
                'image_id': image_id,
                'model_id': model_from_db.id,
                'model_version_id': model_version.id,
                'malignant_detected': bool(malignant_prob >= 0.5),
                'malignant_probability': float(malignant_prob),
                'melanoma_detected': bool(melanoma_prob >= 0.5),
                'melanoma_probability': float(melanoma_prob),
                'predicted_diagnosis': predicted_code,
                'prob_melanoma': float(class4_probs[0]),
                'prob_nevus': float(class4_probs[1]),
                'prob_basal_cell_carcinoma': float(class4_probs[2]),
                'prob_actinic_keratosis': float(class4_probs[3]),
            }
            
            saved_prediction = await uow.predictions.create(prediction_data)
            await uow.commit()

        image_url = f"skin-images/{image_id}"
        
        # 7. Генерируем тепловую карту (если нужно)
        heatmap_url = None
        if generate_heatmap:
            try:
                # Просто вызываем сервис тепловых карт
                heatmap_info = await self.heatmap_service.create_heatmap(
                    model=model,
                    input_tensor=input_tensor,
                    original_image_path=image_path,
                    prediction_id=saved_prediction.id,
                    target_class=None,
                    alpha=0.6
                )
                # Формируем URL
                heatmap_url = f"heatmaps/{heatmap_info['id']}?patient_id={pacient_id}"
            except Exception as e:
                print(f"Heatmap generation failed: {e}")
        
        print(heatmap_url)
        
        # 8. Формируем ответ
        return PredictionResponse(
            id=saved_prediction.id,
            pacient_id=pacient_id,
            image_url=image_url,
            heatmap_url=heatmap_url,
            model=ModelResponseSchema(
                id=model_from_db.id,
                name=model_from_db.name,
                architecture=model_from_db.architecture,
                is_active=model_from_db.is_active,
                current_version=ModelVersionResponseSchema(
                    id=model_version.id,
                    version=model_version.version,
                    file_name=model_version.file_name,
                    file_size=model_version.file_size,
                    created_at=model_version.created_at
                ),
                all_versions=[],
                created_at=model_from_db.created_at,
                updated_at=model_from_db.updated_at
            ),
            malignant=MalignantInfo(
                detected=bool(malignant_prob >= 0.5),
                probability=float(malignant_prob)
            ),
            melanoma=MelanomaInfo(
                detected=bool(melanoma_prob >= 0.5),
                probability=float(melanoma_prob)
            ),
            diagnosis=DiagnosisInfo(
                detected=predicted_code,
                probabilities=DiagnosisProbabilities(
                    melanoma=float(class4_probs[0]),
                    nevus=float(class4_probs[1]),
                    basal_cell_carcinoma=float(class4_probs[2]),
                    actinic_keratosis=float(class4_probs[3])
                )
            ),
            created_at=saved_prediction.created_at
        )
    
    async def _get_model_and_version(self, uow: UnitOfWork, model_id: Optional[int] = None) -> tuple[MLModel, ModelVersion]:
        """Получение модели и её последней версии для инференса"""
        
        if model_id:
            # Получаем конкретную модель по ID
            db_model = await uow.ml_models.get_by_id(model_id)
            if not db_model:
                raise HTTPException(status_code=404, detail=f"Model {model_id} not found")
            
            # Получаем последнюю версию модели
            latest_version = await uow.model_versions.get_latest_version(model_id)
            if not latest_version:
                raise HTTPException(
                    status_code=404,
                    detail=f"No versions found for model {model_id}"
                )
            
            if not latest_version.file_path or not Path(latest_version.file_path).exists():
                raise HTTPException(
                    status_code=404,
                    detail=f"Model file not found for version {latest_version.version} of model {model_id}"
                )
            
            return db_model, latest_version
        else:
            # Получаем глобальную активную модель
            active_model = await uow.ml_models.get_active_model()
            if not active_model:
                raise HTTPException(
                    status_code=404,
                    detail="No active model found in the system"
                )
            
            # Получаем последнюю версию активной модели
            latest_version = await uow.model_versions.get_latest_version(active_model.id)
            if not latest_version:
                raise HTTPException(
                    status_code=404,
                    detail=f"No versions found for active model '{active_model.name}'"
                )
            
            if not latest_version.file_path or not Path(latest_version.file_path).exists():
                raise HTTPException(
                    status_code=404,
                    detail=f"Model file not found for active model '{active_model.name}'"
                )
            
            return active_model, latest_version
    
    async def _load_model(self, model_version: ModelVersion, model_obj: MLModel):
        """Загрузка модели через ModelLoader с кэшированием"""
        try:
            model = self.model_loader.load_model_by_version(
                model_version=model_version,
                model_obj=model_obj,
                strict=False
            )
            return model
        except FileNotFoundError as e:
            raise HTTPException(
                status_code=404,
                detail=f"Model file not found: {str(e)}"
            )
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to load model: {str(e)}"
            )
    
    async def _get_image_path_from_db(self, uow: UnitOfWork, image_id: int, pacient_id: int) -> str:
        """Получение пути к изображению из базы данных"""
        image = await uow.skin_images.get_by_id(image_id)
        
        if not image:
            raise HTTPException(
                status_code=404,
                detail=f"Image {image_id} not found"
            )
        
        if image.patient_id != pacient_id:
            raise HTTPException(
                status_code=403,
                detail=f"Patient {pacient_id} does not have access to image {image_id}"
            )
        
        full_path = Path(settings.upload_dir) / image.file_path
        return str(full_path)

    async def get_patient_predictions_history(
        self,
        patient_id: int,
        current_user_id: int,
        skip: int = 0,
        limit: int = 50
    ) -> PredictionHistoryListResponse:
        """
        Пациент получает историю своих предсказаний
        """
        # Проверяем, что текущий пользователь - это сам пациент
        if current_user_id != patient_id:
            raise HTTPException(
                status_code=403,
                detail="You can only access your own predictions history"
            )
        
        async with self.uow as uow:
            # Получаем предсказания
            predictions, total = await uow.predictions.get_predictions_by_patient(
                patient_id, skip, limit
            )
        
        # Формируем ответ
        history = []
        for pred in predictions:
            history.append(await self._to_history_response(pred))
        
        return PredictionHistoryListResponse(
            total=total,
            skip=skip,
            limit=limit,
            predictions=history
        )
    
    async def get_patient_predictions_for_doctor(
        self,
        doctor_id: int,
        patient_id: int,
        skip: int = 0,
        limit: int = 50
    ) -> PredictionHistoryListResponse:
        """
        Врач получает историю предсказаний своего пациента
        """
        async with self.uow as uow:
            # Проверяем, что врач имеет доступ к пациенту
            doctor_patient = await uow.doctor_patients.get_by_doctor_and_patient(
                doctor_id, patient_id
            )
            if not doctor_patient:
                raise HTTPException(
                    status_code=403,
                    detail="You don't have access to this patient's predictions"
                )
            
            # Получаем предсказания
            predictions, total = await uow.predictions.get_predictions_by_patient(
                patient_id, skip, limit
            )
        
        # Формируем ответ
        history = []
        for pred in predictions:
            history.append(await self._to_history_response(pred))
        
        return PredictionHistoryListResponse(
            total=total,
            skip=skip,
            limit=limit,
            predictions=history
        )
    
    async def _to_history_response(self, prediction: Prediction) -> PredictionResponse:
        """Конвертация предсказания в формат истории"""
        async with self.uow as uow:
            # Получаем информацию о модели
            model_response = None
            if prediction.model:
                # Получаем последнюю версию модели
                latest_version = None
                if prediction.model_version:
                    latest_version = ModelVersionResponseSchema(
                        id=prediction.model_version.id,
                        version=prediction.model_version.version,
                        file_name=prediction.model_version.file_name,
                        file_size=prediction.model_version.file_size,
                        created_at=prediction.model_version.created_at
                    )
                
                # ВАЖНО: Проверяем, что latest_version не None
                # Иначе current_version не передаем
                model_response = ModelResponseSchema(
                    id=prediction.model.id,
                    name=prediction.model.name,
                    architecture=prediction.model.architecture,
                    is_active=prediction.model.is_active,
                    current_version=latest_version,  # Может быть None, это нормально
                    all_versions=[],
                    created_at=prediction.model.created_at,
                    updated_at=prediction.model.updated_at
                )
            
            # Формируем URL изображения
            image_url = f"skin-images/{prediction.image_id}" if prediction.image_id else None
            
            heatmap = None
            heatmap_url = None
            if prediction.id:
                heatmap = await uow.heatmaps.get_latest_by_prediction_id(prediction.id)
                if heatmap:
                    heatmap_url = f"heatmaps/{heatmap.id}?patient_id={prediction.patient_id}"
        
        return PredictionResponse(
            id=prediction.id,
            pacient_id=prediction.patient_id,
            image_url=image_url,
            heatmap_url=heatmap_url,
            model=model_response,
            malignant=MalignantInfo(
                detected=prediction.malignant_detected,
                probability=prediction.malignant_probability
            ),
            melanoma=MelanomaInfo(
                detected=prediction.melanoma_detected,
                probability=prediction.melanoma_probability
            ),
            diagnosis=DiagnosisInfo(
                detected=prediction.predicted_diagnosis,
                probabilities=DiagnosisProbabilities(
                    melanoma=prediction.prob_melanoma,
                    nevus=prediction.prob_nevus,
                    basal_cell_carcinoma=prediction.prob_basal_cell_carcinoma,
                    actinic_keratosis=prediction.prob_actinic_keratosis
                )
            ),
            created_at=prediction.created_at
        )