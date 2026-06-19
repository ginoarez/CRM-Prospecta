import logging

from celery.result import AsyncResult
from fastapi import APIRouter, Depends

from app.api.deps import get_current_user
from app.models import User
from app.schemas.scoring import TaskStatusOut
from app.workers.celery_app import celery

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/tasks", tags=["tasks"])

_STATE_MAP = {
    "PENDING": "pending",
    "RECEIVED": "pending",
    "STARTED": "running",
    "RETRY": "running",
    "SUCCESS": "success",
    "FAILURE": "failure",
    "REVOKED": "failure",
}


def map_celery_state(state: str) -> str:
    return _STATE_MAP.get(state, "pending")


@router.get("/{task_id}", response_model=TaskStatusOut)
def task_status(task_id: str, _: User = Depends(get_current_user)):
    try:
        res = AsyncResult(task_id, app=celery)
        state = res.state
        mapped = map_celery_state(state)
        error = str(res.result) if mapped == "failure" else None
    except Exception as exc:
        logger.warning("task_status fallback for %s: %r", task_id, exc)
        mapped = "pending"
        error = None
    return TaskStatusOut(task_id=task_id, status=mapped, error=error)
