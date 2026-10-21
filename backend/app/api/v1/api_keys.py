from datetime import datetime, timezone
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
import httpx
from app.api.v1.auth import get_current_user
from app.core.security import encrypt_api_key, decrypt_api_key, mask_api_key
from app.db.session import get_db
from app.models.user import User, UserApiKey, ApiKeyCategory, ApiKeyStatus
from app.schemas.app_schemas import (
    ApiKeySaveRequest, ApiKeyResponse, ApiKeyTestRequest,
    ApiKeyTestResponse, PriorityReorderRequest
)

router = APIRouter(prefix="/user/api-keys", tags=["User API Keys (BYOK)"])


@router.get("", response_model=List[ApiKeyResponse])
async def list_user_api_keys(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Lists all stored API keys for the authenticated user with secrets masked."""
    stmt = (
        select(UserApiKey)
        .where(UserApiKey.user_id == current_user.id)
        .order_by(UserApiKey.category.asc(), UserApiKey.priority.asc())
    )
    res = await db.execute(stmt)
    records = res.scalars().all()

    return [
        ApiKeyResponse(
            id=r.id,
            category=r.category.value,
            provider_name=r.provider_name,
            key_preview=r.key_preview,
            priority=r.priority,
            status=r.status.value,
            last_tested_at=r.last_tested_at,
            last_used_at=r.last_used_at,
            error_message=r.error_message,
            quota_limit_hint=r.quota_limit_hint
        )
        for r in records
    ]


@router.put("", response_model=ApiKeyResponse)
async def save_or_update_api_key(
    req: ApiKeySaveRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Encrypts and stores or updates a user BYOK API key."""
    try:
        cat_enum = ApiKeyCategory(req.category.lower())
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": "INVALID_CATEGORY", "message": f"Invalid category: {req.category}"}
        )

    # Check if a key for this user & provider already exists
    stmt = select(UserApiKey).where(
        UserApiKey.user_id == current_user.id,
        UserApiKey.category == cat_enum,
        UserApiKey.provider_name == req.provider_name.lower()
    )
    res = await db.execute(stmt)
    existing = res.scalar_one_or_none()

    encrypted_val = encrypt_api_key(req.api_key.strip())
    preview_val = mask_api_key(req.api_key.strip())

    if existing:
        existing.encrypted_key = encrypted_val
        existing.key_preview = preview_val
        existing.priority = req.priority or existing.priority
        existing.status = ApiKeyStatus.UNTESTED
        existing.error_message = None
        key_record = existing
    else:
        key_record = UserApiKey(
            user_id=current_user.id,
            category=cat_enum,
            provider_name=req.provider_name.lower(),
            encrypted_key=encrypted_val,
            key_preview=preview_val,
            priority=req.priority or 1,
            status=ApiKeyStatus.UNTESTED
        )
        db.add(key_record)

    await db.flush()

    return ApiKeyResponse(
        id=key_record.id,
        category=key_record.category.value,
        provider_name=key_record.provider_name,
        key_preview=key_record.key_preview,
        priority=key_record.priority,
        status=key_record.status.value,
        last_tested_at=key_record.last_tested_at,
        last_used_at=key_record.last_used_at,
        error_message=key_record.error_message,
        quota_limit_hint=key_record.quota_limit_hint
    )


@router.post("/test", response_model=ApiKeyTestResponse)
async def test_api_key(
    req: ApiKeyTestRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Makes a lightweight test call to verify a user-provided API key."""
    raw_key = req.api_key

    # If key is not sent in payload, retrieve user's encrypted key from DB
    key_record = None
    if not raw_key:
        try:
            cat_enum = ApiKeyCategory(req.category.lower())
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid category")

        stmt = select(UserApiKey).where(
            UserApiKey.user_id == current_user.id,
            UserApiKey.category == cat_enum,
            UserApiKey.provider_name == req.provider_name.lower()
        )
        res = await db.execute(stmt)
        key_record = res.scalar_one_or_none()
        if not key_record:
            raise HTTPException(status_code=404, detail="No stored key found to test")
        raw_key = decrypt_api_key(key_record.encrypted_key)

    if not raw_key:
        raise HTTPException(status_code=400, detail="API key is empty")

    provider = req.provider_name.lower()
    start_time = datetime.now()

    # Cheap test ping per provider
    is_valid = True
    message = "Connection successful. Validated with provider."
    try:
        async with httpx.AsyncClient(timeout=8.0) as client:
            if "openweather" in provider:
                test_url = f"https://api.openweathermap.org/data/2.5/weather?lat=24.00&lon=85.36&appid={raw_key}"
                resp = await client.get(test_url)
                if resp.status_code == 401:
                    is_valid = False
                    message = "Invalid API key: Provider returned HTTP 401 Unauthorized"
            elif "openrouter" in provider:
                test_url = "https://openrouter.ai/api/v1/auth/key"
                resp = await client.get(test_url, headers={"Authorization": f"Bearer {raw_key}"})
                if resp.status_code in (401, 403):
                    is_valid = False
                    message = "Invalid OpenRouter API key: HTTP 401 Unauthorized"
            elif "data_gov" in provider:
                test_url = f"https://api.data.gov.in/resource/9ef84268-d588-465a-a308-a864a43d0070?api-key={raw_key}&format=json&limit=1"
                resp = await client.get(test_url)
                if resp.status_code == 403:
                    is_valid = False
                    message = "Invalid data.gov.in API key: HTTP 403 Forbidden"
    except Exception as e:
        is_valid = False
        message = f"Connection test timed out or network error: {str(e)}"

    latency = int((datetime.now() - start_time).total_seconds() * 1000)

    # Update DB record status if testing an existing saved key
    if key_record:
        key_record.last_tested_at = datetime.now(timezone.utc)
        key_record.status = ApiKeyStatus.ACTIVE if is_valid else ApiKeyStatus.INVALID
        key_record.error_message = None if is_valid else message
        await db.flush()

    return ApiKeyTestResponse(
        valid=is_valid,
        status="active" if is_valid else "invalid",
        message=message,
        latency_ms=latency
    )


@router.delete("/{key_id}")
async def delete_api_key(
    key_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Deletes an API key ensuring cross-user IDOR isolation."""
    stmt = select(UserApiKey).where(
        UserApiKey.id == key_id,
        UserApiKey.user_id == current_user.id
    )
    res = await db.execute(stmt)
    key_record = res.scalar_one_or_none()

    if not key_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "KEY_NOT_FOUND", "message": "API key not found"}
        )

    await db.delete(key_record)
    return {"message": "API key removed successfully", "id": key_id}


@router.post("/reorder-priority")
async def reorder_key_priority(
    req: PriorityReorderRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Reorders priority of keys for a category."""
    for priority_idx, key_id in enumerate(req.ordered_key_ids, start=1):
        stmt = select(UserApiKey).where(
            UserApiKey.id == key_id,
            UserApiKey.user_id == current_user.id
        )
        res = await db.execute(stmt)
        record = res.scalar_one_or_none()
        if record:
            record.priority = priority_idx
    await db.flush()
    return {"message": "Key priority updated successfully"}
