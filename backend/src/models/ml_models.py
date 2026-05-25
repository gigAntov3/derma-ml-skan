from sqlalchemy import Column, Integer, String, DateTime, BigInteger, ForeignKey, UniqueConstraint, Index, Boolean, Enum as SQLAlchemyEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from utils.database.engine import Base
import enum


class ModelArchitecture(str, enum.Enum):
    """Архитектуры моделей"""
    RESNET50 = "resnet50"
    EFFICIENTNET_B3 = "efficientnet_b3"
    DENSENET121 = "densenet121"


class MLModel(Base):
    """Таблица моделей"""
    __tablename__ = "ml_models"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True, index=True)
    architecture = Column(SQLAlchemyEnum(ModelArchitecture), nullable=False)
    is_active = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    versions = relationship("ModelVersion", back_populates="model", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<MLModel(id={self.id}, name={self.name}, is_active={self.is_active})>"


class ModelVersion(Base):
    """Таблица версий моделей"""
    __tablename__ = "model_versions"
    
    id = Column(Integer, primary_key=True, index=True)
    model_id = Column(Integer, ForeignKey("ml_models.id", ondelete="CASCADE"), nullable=False)
    version = Column(String(20), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size = Column(BigInteger, nullable=False)
    file_name = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    model = relationship("MLModel", back_populates="versions")
    
    __table_args__ = (
        UniqueConstraint('model_id', 'version', name='uq_model_version'),
        Index('idx_model_versions', 'model_id'),
    )
    
    def __repr__(self):
        return f"<ModelVersion(id={self.id}, model_id={self.model_id}, version={self.version})>"