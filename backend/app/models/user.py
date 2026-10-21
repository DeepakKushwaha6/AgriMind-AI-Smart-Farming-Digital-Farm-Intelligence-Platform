import enum
from datetime import datetime, timezone
from typing import Optional, List
from sqlalchemy import String, Boolean, Integer, DateTime, Enum, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base, TimestampMixin


class UserRole(str, enum.Enum):
    FARMER = "farmer"
    ADMIN = "admin"


class ApiKeyCategory(str, enum.Enum):
    WEATHER = "weather"
    MANDI = "mandi"
    MAPS = "maps"
    SATELLITE = "satellite"
    SOIL = "soil"
    AI = "ai"
    MESSAGING = "messaging"
    NEWS = "news"


class ApiKeyStatus(str, enum.Enum):
    ACTIVE = "active"
    INVALID = "invalid"
    QUOTA_EXCEEDED = "quota_exceeded"
    TESTING = "testing"
    UNTESTED = "untested"


class User(Base, TimestampMixin):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    role: Mapped[UserRole] = mapped_column(Enum(UserRole), default=UserRole.FARMER, nullable=False)
    phone: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    village: Mapped[str] = mapped_column(String(100), default="Jarga")
    district: Mapped[str] = mapped_column(String(100), default="Hazaribagh")
    state: Mapped[str] = mapped_column(String(100), default="Jharkhand")
    lat: Mapped[float] = mapped_column(default=24.002)
    lon: Mapped[float] = mapped_column(default=85.361)
    preferred_language: Mapped[str] = mapped_column(String(10), default="en")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    # Relationships
    farms: Mapped[List["Farm"]] = relationship("Farm", back_populates="owner", cascade="all, delete-orphan")
    api_keys: Mapped[List["UserApiKey"]] = relationship("UserApiKey", back_populates="user", cascade="all, delete-orphan")
    tasks: Mapped[List["Task"]] = relationship("Task", back_populates="user", cascade="all, delete-orphan")
    finances_expenses: Mapped[List["Expense"]] = relationship("Expense", back_populates="user", cascade="all, delete-orphan")
    finances_revenues: Mapped[List["Revenue"]] = relationship("Revenue", back_populates="user", cascade="all, delete-orphan")
    machinery: Mapped[List["Machinery"]] = relationship("Machinery", back_populates="user", cascade="all, delete-orphan")
    soil_records: Mapped[List["SoilRecord"]] = relationship("SoilRecord", back_populates="user", cascade="all, delete-orphan")
    recommendations: Mapped[List["Recommendation"]] = relationship("Recommendation", back_populates="user", cascade="all, delete-orphan")
    chat_sessions: Mapped[List["ChatSession"]] = relationship("ChatSession", back_populates="user", cascade="all, delete-orphan")
    notifications: Mapped[List["Notification"]] = relationship("Notification", back_populates="user", cascade="all, delete-orphan")


class UserApiKey(Base, TimestampMixin):
    """Stores encrypted BYOK API keys strictly isolated per user."""
    __tablename__ = "user_api_keys"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    category: Mapped[ApiKeyCategory] = mapped_column(Enum(ApiKeyCategory), index=True, nullable=False)
    provider_name: Mapped[str] = mapped_column(String(50), nullable=False)  # e.g., openweathermap, data_gov, openrouter
    encrypted_key: Mapped[str] = mapped_column(Text, nullable=False)        # Fernet encrypted ciphertext
    key_preview: Mapped[str] = mapped_column(String(20), nullable=False)    # e.g. "sk-••••4820"
    priority: Mapped[int] = mapped_column(Integer, default=1)               # 1 = primary, 2 = secondary
    status: Mapped[ApiKeyStatus] = mapped_column(Enum(ApiKeyStatus), default=ApiKeyStatus.UNTESTED)
    last_tested_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    last_used_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    error_message: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    quota_limit_hint: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    user: Mapped["User"] = relationship("User", back_populates="api_keys")


class ProviderConfig(Base, TimestampMixin):
    """Global system provider configuration."""
    __tablename__ = "provider_configs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    category: Mapped[ApiKeyCategory] = mapped_column(Enum(ApiKeyCategory), unique=True, nullable=False)
    active_shared_provider: Mapped[str] = mapped_column(String(50), default="free_fallback")
    is_shared_key_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    encrypted_server_key: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    fallback_chain_json: Mapped[str] = mapped_column(Text, default="[]")


class AuditLog(Base, TimestampMixin):
    __tablename__ = "audit_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, index=True)
    action: Mapped[str] = mapped_column(String(100), nullable=False)
    resource_type: Mapped[str] = mapped_column(String(50), nullable=False)
    resource_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    details: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    ip_address: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
