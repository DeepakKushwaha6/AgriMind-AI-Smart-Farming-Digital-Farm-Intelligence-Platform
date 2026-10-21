from typing import Any, Dict
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.v1.auth import get_current_user
from app.db.session import get_db
from app.models.user import User, ApiKeyCategory
from app.schemas.app_schemas import ChatMessageRequest, ChatMessageResponse
from app.services.ai_service import ai_service
from app.services.key_resolver import KeyResolver

router = APIRouter(prefix="/assistant", tags=["AI Assistant"])


@router.post("/chat", response_model=ChatMessageResponse)
async def chat_with_assistant(
    req: ChatMessageRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    user_ai_key = await KeyResolver.get_user_key(db, current_user.id, ApiKeyCategory.AI)
    raw_key = user_ai_key.get("api_key") if user_ai_key else None

    result = await ai_service.query_ai(
        prompt=req.message,
        user_key=raw_key,
        task_category=req.category or "reasoning"
    )

    return ChatMessageResponse(
        text=result["text"],
        model_used=result["model_used"],
        source_type=result["source_type"],
        latency_ms=result["latency_ms"],
        session_id=req.session_id or 1
    )
