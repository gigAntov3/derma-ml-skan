import torch
import torch.nn.functional as F
from pathlib import Path
from typing import Optional, Dict, Any, Tuple
from fastapi import HTTPException
import cv2
import numpy as np
from datetime import datetime

from utils.database.uow import UnitOfWork
from config import settings


class HeatmapService:
    """Сервис для работы с тепловыми картами"""
    
    def __init__(self, uow: UnitOfWork):
        self.uow = uow
        self.heatmaps_dir = Path(settings.upload_dir) / "heatmaps"
        self.heatmaps_dir.mkdir(parents=True, exist_ok=True)
    
    async def create_heatmap(
        self,
        model,
        input_tensor: torch.Tensor,
        original_image_path: str,
        prediction_id: int,
        target_class: Optional[str] = None,
        alpha: float = 0.6
    ) -> Dict[str, Any]:
        """
        Создание и сохранение тепловой карты (полный цикл)
        
        Args:
            model: Загруженная модель
            input_tensor: Предобработанный тензор изображения
            original_image_path: Путь к оригинальному изображению
            prediction_id: ID предсказания
            target_class: Целевой класс ("malignant", "melanoma" или None для auto)
            alpha: Прозрачность наложения
        
        Returns:
            Информация о созданной тепловой карте
        """
        # Генерируем тепловую карту
        heatmap_array = await self._generate_heatmap(model, input_tensor, target_class)
        
        # Накладываем на изображение
        overlay = self._apply_heatmap_overlay(original_image_path, heatmap_array, alpha)
        
        # Сохраняем файл
        filename = f"heatmap_{prediction_id}_{int(datetime.now().timestamp())}.jpg"
        filepath = self.heatmaps_dir / filename
        cv2.imwrite(str(filepath), overlay)
        
        # Сохраняем в БД
        async with self.uow as uow:
            saved_heatmap = await uow.heatmaps.create(
                prediction_id=prediction_id,
                file_path=f"heatmaps/{filename}"
            )
            await uow.commit()
        
        return {
            'id': saved_heatmap.id,
            'prediction_id': saved_heatmap.prediction_id,
            'file_path': saved_heatmap.file_path,
            'created_at': saved_heatmap.created_at
        }
    
    async def create_heatmap_from_array(
        self,
        heatmap_array: np.ndarray,
        original_image_path: str,
        prediction_id: int,
        alpha: float = 0.6
    ) -> Dict[str, Any]:
        """
        Создание тепловой карты из готового массива
        
        Args:
            heatmap_array: Массив тепловой карты (2D numpy array)
            original_image_path: Путь к оригинальному изображению
            prediction_id: ID предсказания
            alpha: Прозрачность наложения
        
        Returns:
            Информация о созданной тепловой карте
        """
        # Накладываем на изображение
        overlay = self._apply_heatmap_overlay(original_image_path, heatmap_array, alpha)
        
        # Сохраняем файл
        filename = f"heatmap_{prediction_id}_{int(datetime.now().timestamp())}.jpg"
        filepath = self.heatmaps_dir / filename
        cv2.imwrite(str(filepath), overlay)
    
        async with self.uow as uow:
            saved_heatmap = await uow.heatmaps.create(
                prediction_id=prediction_id,
                file_path=f"heatmaps/{filename}"
            )
            await uow.commit()
        
        return {
            'id': saved_heatmap.id,
            'prediction_id': saved_heatmap.prediction_id,
            'file_path': saved_heatmap.file_path,
            'created_at': saved_heatmap.created_at
        }
    
    async def _generate_heatmap(
        self,
        model,
        input_tensor: torch.Tensor,
        target_class: Optional[str] = None
    ) -> np.ndarray:
        """
        Генерация Grad-CAM тепловой карты
        
        Args:
            model: Загруженная модель
            input_tensor: Предобработанный тензор изображения
            target_class: Целевой класс ("malignant", "melanoma" или None для auto)
        
        Returns:
            Тепловая карта в виде numpy array
        """
        was_training = model.training
        model.eval()
        
        activations, gradients = [], []
        
        def save_activation(module, inp, out):
            activations.append(out.detach())
        
        def save_gradient(module, grad_inp, grad_out):
            gradients.append(grad_out[0].detach())
        
        # Поиск последнего сверточного слоя
        target_layer = None
        for module in model.modules():
            if isinstance(module, torch.nn.Conv2d):
                target_layer = module
                break
        
        if not target_layer:
            # Если нет сверточного слоя, используем saliency
            model.train() if was_training else None
            return await self._generate_saliency(model, input_tensor, target_class)
        
        # Регистрируем хуки
        hook_fwd = target_layer.register_forward_hook(save_activation)
        hook_bwd = target_layer.register_full_backward_hook(save_gradient)
        
        input_with_grad = input_tensor.clone().detach().requires_grad_(True)
        
        # Forward pass
        malignant, melanoma, class4 = model(input_with_grad)
        
        # Выбираем целевой выход
        target_output = self._get_target_output(malignant, melanoma, class4, target_class)
        
        # Backward pass
        model.zero_grad()
        target_output.backward()
        
        # Получаем активации и градиенты
        if not activations or not gradients:
            hook_fwd.remove()
            hook_bwd.remove()
            model.train() if was_training else None
            return await self._generate_saliency(model, input_tensor, target_class)
        
        act = activations[0]
        grad = gradients[0]
        
        # Удаляем хуки
        hook_fwd.remove()
        hook_bwd.remove()
        
        # Grad-CAM
        weights = grad.mean(dim=[2, 3], keepdim=True)
        cam = F.relu((weights * act).sum(dim=1, keepdim=True))
        cam = cam.squeeze().cpu().numpy()
        
        # Постобработка
        cam = self._postprocess_heatmap(cam)
        
        model.train() if was_training else None
        return cam
    
    async def _generate_saliency(
        self,
        model,
        input_tensor: torch.Tensor,
        target_class: Optional[str] = None
    ) -> np.ndarray:
        """
        Генерация Saliency Map (альтернатива Grad-CAM)
        """
        was_training = model.training
        model.eval()
        
        input_with_grad = input_tensor.clone().detach().requires_grad_(True)
        
        # Forward pass
        malignant, melanoma, class4 = model(input_with_grad)
        
        # Выбираем целевой выход
        target_output = self._get_target_output(malignant, melanoma, class4, target_class)
        
        # Backward pass
        model.zero_grad()
        target_output.backward()
        
        # Получаем салиенси карту
        saliency = input_with_grad.grad.abs().max(dim=1)[0].squeeze().cpu().numpy()
        
        # Нормализация
        if saliency.max() - saliency.min() > 1e-8:
            saliency = (saliency - saliency.min()) / (saliency.max() - saliency.min())
        else:
            saliency = np.zeros_like(saliency)
        
        model.train() if was_training else None
        return saliency
    
    def _get_target_output(self, malignant, melanoma, class4, target_class: Optional[str] = None):
        """
        Выбор целевого выхода для генерации тепловой карты
        """
        if target_class == "malignant":
            return malignant[0, 0]
        elif target_class == "melanoma":
            return melanoma[0, 0]
        else:
            # Автоматически выбираем предсказанный класс
            class_probs = F.softmax(class4, dim=1)
            predicted_class = class_probs.argmax(dim=1).item()
            return class4[0, predicted_class]
    
    def _postprocess_heatmap(self, cam: np.ndarray) -> np.ndarray:
        """
        Постобработка тепловой карты
        """
        # Нормализация с использованием перцентилей
        if cam.max() - cam.min() > 1e-8:
            lower = np.percentile(cam, 10)
            upper = np.percentile(cam, 90)
            cam = (cam - lower) / (upper - lower)
            cam = np.clip(cam, 0, 1)
        else:
            cam = np.zeros_like(cam)
        
        # Усиление контраста
        cam = np.power(cam, 0.7)
        
        # Изменение размера и сглаживание
        cam = cv2.resize(cam, (224, 224))
        cam = cv2.GaussianBlur(cam, (7, 7), 0)
        
        return cam
    
    def _apply_heatmap_overlay(
        self,
        original_image_path: str,
        heatmap_array: np.ndarray,
        alpha: float = 0.6
    ) -> np.ndarray:
        """
        Накладывает тепловую карту на изображение
        """
        # Загружаем оригинальное изображение
        original_image = cv2.imread(original_image_path)
        original_image = cv2.cvtColor(original_image, cv2.COLOR_BGR2RGB)
        
        # Изменяем размер тепловой карты
        heatmap_resized = cv2.resize(
            heatmap_array,
            (original_image.shape[1], original_image.shape[0]),
            interpolation=cv2.INTER_LINEAR
        )
        
        # Нормализация
        if heatmap_resized.max() - heatmap_resized.min() > 1e-8:
            heatmap_resized = (heatmap_resized - heatmap_resized.min()) / (heatmap_resized.max() - heatmap_resized.min())
        else:
            heatmap_resized = np.zeros_like(heatmap_resized)
        
        # Применяем цветовую карту
        heatmap_colored = cv2.applyColorMap(
            np.uint8(255 * heatmap_resized),
            cv2.COLORMAP_JET
        )
        heatmap_colored = cv2.cvtColor(heatmap_colored, cv2.COLOR_BGR2RGB)
        
        # Накладываем с прозрачностью
        overlay = cv2.addWeighted(original_image, 1 - alpha, heatmap_colored, alpha, 0)
        
        return cv2.cvtColor(overlay, cv2.COLOR_RGB2BGR)
    
    async def get_heatmap_by_id(
        self,
        current_user_id: int,
        patient_id: int,
        heatmap_id: int
    ) -> Dict[str, Any]:
        """
        Получение информации о тепловой карте с проверкой прав доступа
        """
        async with self.uow as uow:
            # Получаем тепловую карту
            heatmap = await uow.heatmaps.get_by_id(heatmap_id)
            if not heatmap:
                raise HTTPException(status_code=404, detail="Heatmap not found")
            
            # Получаем предсказание для проверки прав
            prediction = await uow.predictions.get_by_id(heatmap.prediction_id)
            if not prediction:
                raise HTTPException(status_code=404, detail="Prediction not found")
            
            # Проверяем права доступа
            if current_user_id != patient_id:
                doctor_patient = await uow.doctor_patients.get_by_doctor_and_patient(
                    current_user_id, prediction.patient_id
                )
                if not doctor_patient:
                    raise HTTPException(403, "Access denied to this heatmap")
            elif prediction.patient_id != patient_id:
                raise HTTPException(403, "Heatmap does not belong to this patient")
        
        return {
            'id': heatmap.id,
            'prediction_id': heatmap.prediction_id,
            'file_path': heatmap.file_path,
            'created_at': heatmap.created_at
        }
    
    async def get_heatmaps_by_prediction(
        self,
        current_user_id: int,
        patient_id: int,
        prediction_id: int
    ) -> list:
        """
        Получение всех тепловых карт для предсказания
        """
        async with self.uow as uow:
            # Проверяем существование предсказания
            prediction = await uow.predictions.get_by_id(prediction_id)
            if not prediction:
                raise HTTPException(404, "Prediction not found")
            
            # Проверяем права доступа
            if current_user_id != patient_id:
                doctor_patient = await uow.doctor_patients.get_by_doctor_and_patient(
                    current_user_id, prediction.patient_id
                )
                if not doctor_patient:
                    raise HTTPException(403, "Access denied to these heatmaps")
            elif prediction.patient_id != patient_id:
                raise HTTPException(403, "Heatmaps do not belong to this patient")
            
            # Получаем тепловые карты
            heatmaps = await uow.heatmaps.get_by_prediction_id(prediction_id)
        
        return [
            {
                'id': h.id,
                'prediction_id': h.prediction_id,
                'file_path': h.file_path,
                'created_at': h.created_at
            }
            for h in heatmaps
        ]
    
    async def delete_heatmap(
        self,
        current_user_id: int,
        patient_id: int,
        heatmap_id: int
    ) -> Dict[str, str]:
        """
        Удаление тепловой карты
        """
        # Получаем информацию о тепловой карте
        heatmap_info = await self.get_heatmap_by_id(current_user_id, patient_id, heatmap_id)
        
        # Удаляем физический файл
        file_path = Path(settings.upload_dir) / heatmap_info['file_path']
        if file_path.exists():
            file_path.unlink()
        
        # Удаляем запись из БД
        async with self.uow as uow:
            await uow.heatmaps.delete(heatmap_id)
            await uow.commit()
        
        return {'message': f"Heatmap {heatmap_id} deleted successfully"}
    
    async def get_heatmap_file_path(self, heatmap_id: int) -> Path:
        """
        Получение пути к файлу тепловой карты
        """
        async with self.uow as uow:
            heatmap = await uow.heatmaps.get_by_id(heatmap_id)
            if not heatmap:
                raise HTTPException(404, "Heatmap not found")
        
        file_path = Path(settings.upload_dir) / heatmap.file_path
        if not file_path.exists():
            raise HTTPException(404, "Heatmap file not found")
        
        return file_path