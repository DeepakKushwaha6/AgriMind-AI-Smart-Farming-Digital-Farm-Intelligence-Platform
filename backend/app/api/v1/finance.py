from datetime import date
from typing import Any, Dict, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.v1.auth import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.models.finance import Expense, Revenue
from app.schemas.app_schemas import FinanceCreateRequest

router = APIRouter(prefix="/finance", tags=["Finance & ROI"])


@router.get("/ledger", response_model=List[Dict[str, Any]])
async def get_financial_ledger(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    exp_res = await db.execute(select(Expense).where(Expense.user_id == current_user.id).order_by(Expense.date.desc()))
    expenses = exp_res.scalars().all()

    rev_res = await db.execute(select(Revenue).where(Revenue.user_id == current_user.id).order_by(Revenue.date.desc()))
    revenues = rev_res.scalars().all()

    entries = []
    for e in expenses:
        entries.append({
            "id": f"FIN-EXP-{e.id}",
            "date": str(e.date),
            "type": "Expense",
            "category": e.category,
            "item": e.item_description,
            "field": e.field_name,
            "planned": e.planned_amount,
            "actual": e.actual_amount
        })

    for r in revenues:
        entries.append({
            "id": f"FIN-REV-{r.id}",
            "date": str(r.date),
            "type": "Revenue",
            "category": r.category,
            "item": r.item_description,
            "field": r.field_name,
            "planned": r.planned_amount,
            "actual": r.actual_amount
        })

    entries.sort(key=lambda x: x["date"], reverse=True)
    return entries


@router.post("/entry", response_model=Dict[str, Any])
async def create_finance_entry(
    req: FinanceCreateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    entry_date = req.date or date.today()
    if req.type.lower() == "revenue":
        rev = Revenue(
            user_id=current_user.id,
            date=entry_date,
            category=req.category,
            item_description=req.item_description,
            field_name=req.field_name or "Plot A",
            planned_amount=req.planned_amount,
            actual_amount=req.actual_amount
        )
        db.add(rev)
        await db.flush()
        return {"id": f"FIN-REV-{rev.id}", "type": "Revenue", "amount": rev.actual_amount}
    else:
        exp = Expense(
            user_id=current_user.id,
            date=entry_date,
            category=req.category,
            item_description=req.item_description,
            field_name=req.field_name or "Plot A",
            planned_amount=req.planned_amount,
            actual_amount=req.actual_amount
        )
        db.add(exp)
        await db.flush()
        return {"id": f"FIN-EXP-{exp.id}", "type": "Expense", "amount": exp.actual_amount}
