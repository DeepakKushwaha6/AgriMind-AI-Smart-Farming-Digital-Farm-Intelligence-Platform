from typing import List, Any, Dict
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.v1.auth import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.models.machinery import Machinery

router = APIRouter(prefix="/machinery", tags=["Machinery"])


class MachineryCreate(BaseModel):
    name: str = Field(..., example="12 HP Power Tiller")
    mode: str = Field("Owned", example="Owned")
    cost_per_hr: float = Field(280.0, example=280.0)
    custom_hire_rate_hr: float = Field(650.0, example=650.0)
    hours_used_season: float = Field(0.0)
    fuel_litres_hr: float = Field(1.4)
    status: str = Field("Operational")


class MachineryOut(BaseModel):
    id: int
    name: str
    mode: str
    cost_per_hr: float
    custom_hire_rate_hr: float
    hours_used_season: float
    fuel_litres_hr: float
    status: str

    class Config:
        from_attributes = True


@router.get("", response_model=List[MachineryOut])
async def list_machinery(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(Machinery).where(Machinery.user_id == current_user.id)
    res = await db.execute(stmt)
    return res.scalars().all()


@router.post("", response_model=MachineryOut, status_code=status.HTTP_201_CREATED)
async def create_machinery(
    payload: MachineryCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    machine = Machinery(
        user_id=current_user.id,
        name=payload.name,
        mode=payload.mode,
        cost_per_hr=payload.cost_per_hr,
        custom_hire_rate_hr=payload.custom_hire_rate_hr,
        hours_used_season=payload.hours_used_season,
        fuel_litres_hr=payload.fuel_litres_hr,
        status=payload.status
    )
    db.add(machine)
    await db.commit()
    await db.refresh(machine)
    return machine


@router.delete("/{machine_id}")
async def delete_machinery(
    machine_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(Machinery).where(Machinery.id == machine_id, Machinery.user_id == current_user.id)
    res = await db.execute(stmt)
    machine = res.scalars().first()
    if not machine:
        raise HTTPException(status_code=404, detail="Machinery item not found")
    await db.delete(machine)
    await db.commit()
    return {"message": "Machinery item deleted successfully"}
