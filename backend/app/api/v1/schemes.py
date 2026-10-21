from typing import Any, Dict, List
from fastapi import APIRouter, Depends
from app.api.v1.auth import get_current_user
from app.connectors.schemes_connector import SchemesConnector
from app.models.user import User

router = APIRouter(prefix="/schemes", tags=["Government Schemes"])
schemes_connector = SchemesConnector()


@router.get("", response_model=List[Dict[str, Any]])
async def list_schemes(current_user: User = Depends(get_current_user)):
    return await schemes_connector.get_verified_schemes()
