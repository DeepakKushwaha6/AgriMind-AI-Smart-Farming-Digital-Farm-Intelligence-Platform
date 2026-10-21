from fastapi import APIRouter
from app.api.v1.auth import router as auth_router
from app.api.v1.api_keys import router as api_keys_router
from app.api.v1.farms import router as farms_router
from app.api.v1.dashboard import router as dashboard_router
from app.api.v1.weather import router as weather_router
from app.api.v1.market import router as market_router
from app.api.v1.location import router as location_router
from app.api.v1.soil import router as soil_router
from app.api.v1.tasks import router as tasks_router
from app.api.v1.finance import router as finance_router
from app.api.v1.recommendations import router as recommendations_router
from app.api.v1.assistant import router as assistant_router
from app.api.v1.schemes import router as schemes_router
from app.api.v1.admin import router as admin_router
from app.api.v1.machinery import router as machinery_router

api_v1_router = APIRouter(prefix="/api/v1")

api_v1_router.include_router(auth_router)
api_v1_router.include_router(api_keys_router)
api_v1_router.include_router(farms_router)
api_v1_router.include_router(dashboard_router)
api_v1_router.include_router(weather_router)
api_v1_router.include_router(market_router)
api_v1_router.include_router(location_router)
api_v1_router.include_router(soil_router)
api_v1_router.include_router(tasks_router)
api_v1_router.include_router(finance_router)
api_v1_router.include_router(machinery_router)
api_v1_router.include_router(recommendations_router)
api_v1_router.include_router(assistant_router)
api_v1_router.include_router(schemes_router)
api_v1_router.include_router(admin_router)

