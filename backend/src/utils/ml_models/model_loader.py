import torch
from typing import Optional, Dict, Any
from pathlib import Path
from collections import OrderedDict
import re

from models.ml_models import MLModel, ModelVersion
from utils.ml_models.architecture import MLModelArchitecture


class ModelLoader:
    def __init__(self, device: Optional[str] = None, cache_size: int = 5):
        if device is None:
            self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        else:
            self.device = torch.device(device)
        
        self.cache_size = cache_size
        self._model_cache: OrderedDict[str, torch.nn.Module] = OrderedDict()
    
    def _get_cache_key(self, model_id: int, version_id: int) -> str:
        """Создание ключа для кэша"""
        return f"{model_id}_{version_id}"
    
    def load_model(
        self,
        model_obj: MLModel,
        version: Optional[ModelVersion] = None,
        strict: bool = False,
        map_location: Optional[str] = None,
        use_cache: bool = True
    ):
        """
        Загрузка модели с автоматическим определением архитектуры из checkpoint
        """
        # Определяем путь к файлу и ключ кэша
        file_path = version.file_path if version else model_obj.file_path
        cache_key = self._get_cache_key(model_obj.id, version.id if version else 0)
        
        # Проверяем кэш
        if use_cache and cache_key in self._model_cache:
            print(f"✓ Loading model from cache: {cache_key}")
            return self._model_cache[cache_key]
        
        # Загружаем checkpoint
        load_device = map_location if map_location else self.device
        checkpoint_path = Path(file_path)
        
        if not checkpoint_path.exists():
            raise FileNotFoundError(f"Checkpoint not found: {checkpoint_path}")
        
        print(f"Loading checkpoint from: {checkpoint_path}")
        checkpoint = torch.load(checkpoint_path, map_location=load_device)
        
        # Извлекаем state_dict
        state_dict = self._extract_state_dict(checkpoint)
        state_dict = self._remove_dataparallel_wrapper(state_dict)
        
        # Определяем реальную архитектуру из checkpoint
        cnn_backbone = self._detect_cnn_backbone_from_state_dict(state_dict)
        vit_model = self._detect_vit_model_from_state_dict(state_dict)
        fusion_dim = self._detect_fusion_dim(state_dict)
        dropout_rate = self._detect_dropout_rate(state_dict)
        
        print(f"✓ Detected from checkpoint:")
        print(f"  - CNN backbone: {cnn_backbone}")
        print(f"  - ViT model: {vit_model}")
        print(f"  - Fusion dimension: {fusion_dim}")
        print(f"  - Dropout rate: {dropout_rate}")
        
        # Создаем модель с правильной архитектурой (всегда pretrained=False для загрузки весов)
        model = MLModelArchitecture(
            cnn_backbone=cnn_backbone,
            vit_model=vit_model,
            num_classes_4class=4,
            pretrained=False,  # Важно: False, так как загружаем свои веса
            dropout_rate=dropout_rate,
            fusion_dim=fusion_dim
        )
        
        # Загружаем веса
        try:
            missing_keys, unexpected_keys = model.load_state_dict(state_dict, strict=strict)
            
            if missing_keys:
                print(f"  ⚠️ Missing keys ({len(missing_keys)}): {missing_keys[:5]}...")
            if unexpected_keys:
                print(f"  ⚠️ Unexpected keys ({len(unexpected_keys)}): {unexpected_keys[:5]}...")
                
            # Если слишком много missing keys, возможно проблема с архитектурой
            if len(missing_keys) > 20:
                raise RuntimeError(f"Too many missing keys ({len(missing_keys)}). Architecture mismatch!")
                
        except Exception as e:
            print(f"❌ Failed to load state_dict: {e}")
            raise
        
        model.to(self.device)
        model.eval()
        
        # Кэшируем
        if use_cache:
            self._add_to_cache(cache_key, model)
        
        print(f"✓ Model loaded successfully on {self.device}")
        return model
    
    def _detect_cnn_backbone_from_state_dict(self, state_dict: Dict) -> str:
        """Определяет CNN backbone по весам"""
        # Проверяем ключи для разных архитектур
        
        # ResNet family
        if 'cnn.conv1.weight' in state_dict:
            out_channels = state_dict['cnn.conv1.weight'].shape[0]
            if out_channels == 64:
                # ResNet50 или ResNet101
                if 'cnn.layer4.0.conv1.weight' in state_dict:
                    # Проверяем количество каналов в layer4
                    layer4_channels = state_dict['cnn.layer4.0.conv1.weight'].shape[0]
                    if layer4_channels == 512:
                        return 'resnet50'
                    elif layer4_channels == 1024:
                        return 'resnet101'
                return 'resnet50'
        
        # DenseNet family
        if 'cnn.features.denseblock1.denselayer1.conv1.weight' in state_dict:
            # Проверяем classifier вес для определения версии
            if 'cnn.classifier.weight' in state_dict:
                in_features = state_dict['cnn.classifier.weight'].shape[1]
                if in_features == 1024:
                    return 'densenet121'
                elif in_features == 1664:
                    return 'densenet169'
            return 'densenet121'
        
        # EfficientNet
        if 'cnn.conv_stem.weight' in state_dict:
            return 'efficientnet_b3'
        
        # Поиск по размерности признаков
        cnn_dim = self._detect_cnn_output_dim(state_dict)
        if cnn_dim == 1024:
            return 'densenet121'
        elif cnn_dim == 1664:
            return 'densenet169'
        elif cnn_dim == 2048:
            return 'resnet50'
        elif cnn_dim == 1536:
            return 'efficientnet_b3'
        
        # По умолчанию
        print("  ⚠️ Could not detect CNN backbone, using 'resnet50'")
        return 'resnet50'
    
    def _detect_cnn_output_dim(self, state_dict: Dict) -> int:
        """Определяет выходную размерность CNN по весам fusion слоя"""
        if 'fusion.0.weight' in state_dict:
            # fusion.0.weight имеет форму [fusion_dim, cnn_dim + vit_dim]
            total_dim = state_dict['fusion.0.weight'].shape[1]
            
            # Определяем vit_dim
            vit_dim = self._get_vit_dim_from_state_dict(state_dict)
            
            # Вычисляем cnn_dim
            cnn_dim = total_dim - vit_dim
            return cnn_dim
        return 2048  # default
    
    def _get_vit_dim_from_state_dict(self, state_dict: Dict) -> int:
        """Определяет размерность ViT из state_dict"""
        if 'vit.cls_token' in state_dict:
            return state_dict['vit.cls_token'].shape[1]
        return 384  # default vit_small
    
    def _detect_vit_model_from_state_dict(self, state_dict: Dict) -> str:
        """Определяет ViT модель по весам"""
        if 'vit.cls_token' in state_dict:
            dim = state_dict['vit.cls_token'].shape[1]
            if dim == 384:
                return 'vit_small_patch16_224'
            elif dim == 768:
                return 'vit_base_patch16_224'
            elif dim == 192:
                return 'vit_tiny_patch16_224'
        
        # Пробуем определить по fusion слою
        if 'fusion.0.weight' in state_dict:
            total_dim = state_dict['fusion.0.weight'].shape[1]
            cnn_dim = self._detect_cnn_output_dim(state_dict)
            vit_dim = total_dim - cnn_dim
            if vit_dim == 384:
                return 'vit_small_patch16_224'
            elif vit_dim == 768:
                return 'vit_base_patch16_224'
            elif vit_dim == 192:
                return 'vit_tiny_patch16_224'
        
        return 'vit_small_patch16_224'
    
    def _detect_fusion_dim(self, state_dict: Dict) -> int:
        """Определяет размер fusion слоя"""
        if 'fusion.0.weight' in state_dict:
            return state_dict['fusion.0.weight'].shape[0]
        return 512
    
    def _detect_dropout_rate(self, state_dict: Dict) -> float:
        """Пытается определить dropout rate из state_dict"""
        # По умолчанию возвращаем стандартное значение
        # Точное определение dropout rate из весов невозможно,
        # но можно попробовать найти по ключам BatchNorm
        if 'fusion.1.weight' in state_dict:
            # Если есть BatchNorm, значит dropout скорее всего 0.3
            return 0.3
        return 0.3
    
    def load_model_by_version(
        self,
        model_version: ModelVersion,
        model_obj: Optional[MLModel] = None,
        strict: bool = False,
        use_cache: bool = True
    ):
        """
        Загрузка модели по версии с автоматическим определением архитектуры
        """
        # Если модель не передана, предполагаем, что она доступна как атрибут
        if model_obj is None and hasattr(model_version, 'model'):
            model_obj = model_version.model
        elif model_obj is None:
            raise ValueError("model_obj is required when model_version doesn't have model attribute")
        
        return self.load_model(model_obj, model_version, strict, use_cache=use_cache)
    
    def _extract_state_dict(self, checkpoint: Any) -> Dict:
        """Извлечение state_dict из checkpoint"""
        if isinstance(checkpoint, dict):
            if 'model_state_dict' in checkpoint:
                return checkpoint['model_state_dict']
            elif 'state_dict' in checkpoint:
                return checkpoint['state_dict']
            elif 'model' in checkpoint:
                return checkpoint['model']
            else:
                # Предполагаем, что сам checkpoint и есть state_dict
                # Проверяем, что ключи выглядят как веса модели
                if any(k.startswith('cnn.') or k.startswith('vit.') or k.startswith('fusion.') 
                       for k in checkpoint.keys()):
                    return checkpoint
                else:
                    raise ValueError(f"Unknown checkpoint format. Keys: {list(checkpoint.keys())[:10]}")
        return checkpoint
    
    def _remove_dataparallel_wrapper(self, state_dict: Dict) -> Dict:
        """Удаление 'module.' из ключей state_dict"""
        new_state_dict = {}
        for k, v in state_dict.items():
            # Удаляем 'module.' в начале
            name = re.sub(r'^module\.', '', k)
            # Удаляем '_orig_mod.' (для torch.compile)
            name = re.sub(r'^_orig_mod\.', '', name)
            new_state_dict[name] = v
        return new_state_dict
    
    def _add_to_cache(self, cache_key: str, model: torch.nn.Module):
        """Добавление модели в кэш с LRU политикой"""
        # Если ключ уже существует, удаляем его (обновляем позицию)
        if cache_key in self._model_cache:
            del self._model_cache[cache_key]
        
        # Если кэш переполнен, удаляем самую старую модель
        elif len(self._model_cache) >= self.cache_size:
            oldest_key = next(iter(self._model_cache))
            removed = self._model_cache.pop(oldest_key)
            print(f"  Cache full. Removed oldest model: {oldest_key}")
            # Очищаем память GPU при необходимости
            if torch.cuda.is_available():
                del removed
                torch.cuda.empty_cache()
        
        self._model_cache[cache_key] = model
        print(f"  Added model to cache: {cache_key} (cache size: {len(self._model_cache)}/{self.cache_size})")
    
    def get_cached_model(self, model_id: int, version_id: int) -> Optional[torch.nn.Module]:
        """Получение модели из кэша"""
        cache_key = self._get_cache_key(model_id, version_id)
        return self._model_cache.get(cache_key)
    
    def is_cached(self, model_id: int, version_id: int) -> bool:
        """Проверка наличия модели в кэше"""
        cache_key = self._get_cache_key(model_id, version_id)
        return cache_key in self._model_cache
    
    def clear_cache(self):
        """Полная очистка кэша"""
        cache_size = len(self._model_cache)
        self._model_cache.clear()
        
        # Очищаем GPU память
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        
        print(f"Model cache cleared. Removed {cache_size} models.")
    
    def remove_from_cache(self, model_id: int, version_id: int) -> bool:
        """Удаление конкретной модели из кэша"""
        cache_key = self._get_cache_key(model_id, version_id)
        if cache_key in self._model_cache:
            del self._model_cache[cache_key]
            print(f"Removed model {cache_key} from cache")
            return True
        return False
    
    def get_cache_info(self) -> Dict:
        """Получение информации о кэше"""
        return {
            "cached_models_count": len(self._model_cache),
            "max_cache_size": self.cache_size,
            "cached_keys": list(self._model_cache.keys()),
            "cache_usage_percent": (len(self._model_cache) / self.cache_size) * 100 if self.cache_size > 0 else 0
        }
    
    def set_cache_size(self, new_size: int):
        """Изменение размера кэша"""
        if new_size < 1:
            raise ValueError("Cache size must be at least 1")
        
        self.cache_size = new_size
        
        # Если текущий кэш больше нового размера, удаляем лишние модели
        while len(self._model_cache) > self.cache_size:
            oldest_key = next(iter(self._model_cache))
            del self._model_cache[oldest_key]
        
        print(f"Cache size changed to {new_size}")