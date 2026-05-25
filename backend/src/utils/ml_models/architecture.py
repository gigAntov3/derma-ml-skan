import torch
import torch.nn as nn
import timm

from typing import Literal, Tuple

class MLModelArchitecture(nn.Module):
    def __init__(
        self,
        cnn_backbone: Literal['resnet50', 'resnet101', 'densenet121', 'densenet169', 'efficientnet_b3'] = 'resnet50',
        vit_model: str = 'vit_small_patch16_224',
        num_classes_4class: int = 4,
        pretrained: bool = True,
        dropout_rate: float = 0.3,
        fusion_dim: int = 512
    ):
        super().__init__()
        
        # === CNN бэкбон ===
        self.cnn_backbone_name = cnn_backbone
        self.cnn = timm.create_model(cnn_backbone, pretrained=pretrained, num_classes=0)
        self.cnn_dim = self._get_cnn_output_dim(cnn_backbone)
        
        # === ViT бэкбон ===
        self.vit = timm.create_model(vit_model, pretrained=pretrained, num_classes=0)
        self.vit_dim = self._get_vit_dim(vit_model)
        
        # === Fusion блок ===
        fusion_input_dim = self.cnn_dim + self.vit_dim
        self.fusion = nn.Sequential(
            nn.Linear(fusion_input_dim, fusion_dim),
            nn.BatchNorm1d(fusion_dim),
            nn.ReLU(inplace=True),
            nn.Dropout(dropout_rate),
            nn.Linear(fusion_dim, fusion_dim // 2),
            nn.BatchNorm1d(fusion_dim // 2),
            nn.ReLU(inplace=True),
            nn.Dropout(dropout_rate / 2)
        )
        
        # === Три головы ===
        # 1. Бинарная: злокачественная / доброкачественная
        self.head_binary_malignant = nn.Sequential(
            nn.Linear(fusion_dim // 2, 64),
            nn.ReLU(inplace=True),
            nn.Dropout(0.2),
            nn.Linear(64, 1)
        )
        
        # 2. Бинарная: меланома / не меланома
        self.head_binary_melanoma = nn.Sequential(
            nn.Linear(fusion_dim // 2, 64),
            nn.ReLU(inplace=True),
            nn.Dropout(0.2),
            nn.Linear(64, 1)
        )
        
        # 3. 4-х классовая
        self.head_4class = nn.Sequential(
            nn.Linear(fusion_dim // 2, 128),
            nn.ReLU(inplace=True),
            nn.Dropout(0.2),
            nn.Linear(128, num_classes_4class)
        )
    
    def _get_cnn_output_dim(self, backbone: str) -> int:
        dims = {
            'resnet50': 2048,
            'resnet101': 2048,
            'densenet121': 1024,
            'densenet169': 1664,
            'efficientnet_b3': 1536,
        }
        return dims.get(backbone, 2048)
    
    def _get_vit_dim(self, vit_model: str) -> int:
        dims = {
            'vit_small_patch16_224': 384,
            'vit_base_patch16_224': 768,
            'vit_tiny_patch16_224': 192
        }
        return dims.get(vit_model, 384)
    
    def forward(self, x: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        # Извлечение признаков
        cnn_features = self.cnn(x)
        
        # Для ViT используем forward_features если доступен
        if hasattr(self.vit, 'forward_features'):
            vit_features = self.vit.forward_features(x)
            # ViT может возвращать последовательность токенов, берем cls токен
            if vit_features.dim() == 3:
                vit_features = vit_features[:, 0]  # CLS token
        else:
            vit_features = self.vit(x)
        
        # Конкатенация
        combined = torch.cat([cnn_features, vit_features], dim=1)
        
        # Fusion
        fused = self.fusion(combined)
        
        # Выходы (без Sigmoid для численной стабильности)
        malignant = self.head_binary_malignant(fused)
        melanoma = self.head_binary_melanoma(fused)
        class4 = self.head_4class(fused)
        
        return malignant, melanoma, class4
    
    def get_features(self, x: torch.Tensor) -> torch.Tensor:
        """Возвращает fusion features для визуализации"""
        cnn_features = self.cnn(x)
        
        if hasattr(self.vit, 'forward_features'):
            vit_features = self.vit.forward_features(x)
            if vit_features.dim() == 3:
                vit_features = vit_features[:, 0]
        else:
            vit_features = self.vit(x)
        
        combined = torch.cat([cnn_features, vit_features], dim=1)
        return self.fusion(combined)