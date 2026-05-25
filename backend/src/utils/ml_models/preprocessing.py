import torch
import torchvision.transforms as transforms
from PIL import Image
from typing import Union, Optional
import numpy as np
import cv2

class ImagePreprocessor:
    """Препроцессор изображений для моделей классификации"""
    
    def __init__(self, target_size: tuple = (224, 224), normalize: bool = True):
        """
        Инициализация препроцессора
        
        Args:
            target_size: размер выходного изображения (height, width)
            normalize: применять ли нормализацию ImageNet
        """
        self.target_size = target_size
        
        # Стандартные нормализации для ImageNet
        self.mean = [0.485, 0.456, 0.406]
        self.std = [0.229, 0.224, 0.225]
        
        # Базовые трансформации
        if normalize:
            self.transform = transforms.Compose([
                transforms.Resize(target_size),
                transforms.ToTensor(),
                transforms.Normalize(mean=self.mean, std=self.std)
            ])
        else:
            self.transform = transforms.Compose([
                transforms.Resize(target_size),
                transforms.ToTensor()
            ])
    
    def preprocess(self, image_path: str) -> torch.Tensor:
        """
        Загрузка и предобработка изображения из файла
        
        Args:
            image_path: путь к изображению
            
        Returns:
            torch.Tensor: тензор размера [1, 3, height, width]
        """
        # Загружаем изображение
        image = Image.open(image_path).convert('RGB')
        
        # Применяем трансформации
        tensor = self.transform(image)
        
        # Добавляем batch dimension
        tensor = tensor.unsqueeze(0)
        
        return tensor
    


# Failed to load model: Error(s) in loading state_dict for MLModelArchitecture: size mismatch for fusion.0.weight: copying a param with shape torch.Size([512, 1408]) from checkpoint, the shape in current model is torch.Size([512, 2432]