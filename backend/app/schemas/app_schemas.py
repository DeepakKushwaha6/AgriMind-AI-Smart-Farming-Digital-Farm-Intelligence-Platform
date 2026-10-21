from datetime import date, datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, EmailStr, Field


# Auth Schemas
class UserRegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
    name: str = Field(min_length=2)
    phone: Optional[str] = None
    village: Optional[str] = "Jarga"
    district: Optional[str] = "Hazaribagh"
    state: Optional[str] = "Jharkhand"


class UserLoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    refresh_token: str
    expires_in_seconds: int = 900
    user: Dict[str, Any]


class UserResponse(BaseModel):
    id: int
    email: str
    name: str
    role: str
    phone: Optional[str] = None
    village: str
    district: str
    state: str
    lat: float
    lon: float
    preferred_language: str


class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str = Field(min_length=8)


# BYOK API Key Schemas
class ApiKeySaveRequest(BaseModel):
    category: str      # weather, mandi, maps, satellite, soil, ai, messaging, news
    provider_name: str # e.g. openweathermap, data_gov, openrouter
    api_key: str = Field(min_length=4)
    priority: Optional[int] = 1


class ApiKeyResponse(BaseModel):
    id: int
    category: str
    provider_name: str
    key_preview: str   # Masked, e.g. sk-••••4820
    priority: int
    status: str
    last_tested_at: Optional[datetime] = None
    last_used_at: Optional[datetime] = None
    error_message: Optional[str] = None
    quota_limit_hint: Optional[str] = None


class ApiKeyTestRequest(BaseModel):
    category: str
    provider_name: str
    api_key: Optional[str] = None  # If None, tests the stored key


class ApiKeyTestResponse(BaseModel):
    valid: bool
    status: str
    message: str
    latency_ms: int


class PriorityReorderRequest(BaseModel):
    category: str
    ordered_key_ids: List[int]


# Farm & Field Schemas
class FieldCreateRequest(BaseModel):
    farm_id: Optional[int] = None
    name: str
    area_acres: float
    soil_type: Optional[str] = "Clay Loam (pH 6.1)"
    water_source: Optional[str] = "Solar Borewell"
    crop: Optional[str] = "Paddy (Sahbhagi Dhan)"
    variety: Optional[str] = "Sahbhagi Dhan"
    lat: Optional[float] = 24.002
    lon: Optional[float] = 85.361


class FieldResponse(BaseModel):
    id: int
    code: str
    name: str
    area_acres: float
    area_katha: float
    area_hectares: float
    soil_type: str
    water_source: str
    crop: str
    variety: str
    stage: str
    days_old: int
    soil_moisture_pct: int
    moisture_source: str
    ndvi: float
    ndwi: float
    status: str
    expected_yield_qtl: float
    expected_profit_inr: float


# Weather Schemas
class DailyForecastItem(BaseModel):
    day: str
    date: str
    temp_max: int
    temp_min: int
    rain_mm: float
    pop: int
    wind: int
    cond: str
    icon: str
    spray_safe: bool


class WeatherResponse(BaseModel):
    location: str
    temp_c: int
    humidity: int
    condition: str
    wind_kph: float
    rain_7d_mm: float
    rain_trend: str
    et0_mm_day: float
    soil_moisture_pct: int
    irrigation_due_days: int
    irrigation_due_date: str
    daily_forecast: List[DailyForecastItem]
    source: str
    source_type: str
    freshness: str
    is_stale: bool


# Market Schemas
class MandiPriceItem(BaseModel):
    id: str
    mandi: str
    district: str
    state: str
    commodity: str
    variety: str
    modal_price: float
    min_price: float
    max_price: float
    arrivals_ton: float
    distance_km: float
    transport_per_qtl: float
    handling_per_qtl: float
    change_pct: str
    net_realisation_per_qtl: float
    source: str
    source_type: str
    freshness: str
    url: str


class NetRealisationCalcRequest(BaseModel):
    quantity_qtl: float
    mandi_modal_price: float
    distance_km: float
    transport_rate_per_km_qtl: Optional[float] = 0.9
    handling_per_qtl: Optional[float] = 20.0
    commission_pct: Optional[float] = 1.0


class NetRealisationCalcResponse(BaseModel):
    gross_revenue: float
    transport_deduction: float
    handling_deduction: float
    commission_deduction: float
    total_deductions: float
    net_realisation: float
    net_per_qtl: float


# Task & Finance Schemas
class TaskCreateRequest(BaseModel):
    title: str
    description: Optional[str] = None
    due_date: date
    field_name: Optional[str] = "Plot A — North Lowland"
    category: Optional[str] = "Agronomy"
    priority: Optional[str] = "Medium"


class FinanceCreateRequest(BaseModel):
    type: str  # Expense or Revenue
    category: str
    item_description: str
    field_name: Optional[str] = "Plot A"
    planned_amount: float
    actual_amount: float
    date: Optional[date] = None


# AI & Recommendation Schemas
class RecommendationGenerateRequest(BaseModel):
    field_id: Optional[int] = None
    question: Optional[str] = None
    task_category: Optional[str] = "reasoning"


class ChatMessageRequest(BaseModel):
    message: str
    category: Optional[str] = "reasoning"
    session_id: Optional[int] = None


class ChatMessageResponse(BaseModel):
    text: str
    model_used: str
    source_type: str
    latency_ms: int
    session_id: int
