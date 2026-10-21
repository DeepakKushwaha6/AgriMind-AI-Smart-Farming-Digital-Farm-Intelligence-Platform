from typing import Any, Dict, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.v1.auth import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.models.task import Task
from app.schemas.app_schemas import TaskCreateRequest

router = APIRouter(prefix="/tasks", tags=["Tasks & Calendar"])


@router.get("", response_model=List[Dict[str, Any]])
async def list_tasks(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    stmt = (
        select(Task)
        .where(Task.user_id == current_user.id)
        .order_by(Task.is_done.asc(), Task.due_date.asc())
    )
    res = await db.execute(stmt)
    tasks = res.scalars().all()

    return [
        {
            "id": f"TSK-{t.id}",
            "db_id": t.id,
            "title": t.title,
            "desc": t.description or "",
            "date": t.due_date.strftime("%d %B %Y"),
            "field": t.field_name,
            "category": t.category,
            "priority": t.priority,
            "done": t.is_done
        }
        for t in tasks
    ]


@router.post("", response_model=Dict[str, Any])
async def create_task(
    req: TaskCreateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    new_task = Task(
        user_id=current_user.id,
        title=req.title,
        description=req.description,
        due_date=req.due_date,
        field_name=req.field_name or "Plot A — North Lowland",
        category=req.category or "Agronomy",
        priority=req.priority or "Medium"
    )
    db.add(new_task)
    await db.flush()

    return {
        "id": f"TSK-{new_task.id}",
        "db_id": new_task.id,
        "title": new_task.title,
        "done": False,
        "message": "Task added to crop calendar"
    }


@router.patch("/{task_id}/toggle", response_model=Dict[str, Any])
async def toggle_task(
    task_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(Task).where(Task.id == task_id, Task.user_id == current_user.id)
    res = await db.execute(stmt)
    task = res.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    task.is_done = not task.is_done
    await db.flush()
    return {"id": f"TSK-{task.id}", "done": task.is_done}


@router.delete("/{task_id}")
async def delete_task(
    task_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(Task).where(Task.id == task_id, Task.user_id == current_user.id)
    res = await db.execute(stmt)
    task = res.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    await db.delete(task)
    return {"message": "Task deleted successfully"}
