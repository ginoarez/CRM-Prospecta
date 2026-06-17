from celery import Celery

from app.core.config import settings

celery = Celery("prospecta", broker=settings.REDIS_URL, backend=settings.REDIS_URL)
celery.conf.update(task_track_started=True)

import app.workers.tasks  # noqa: E402,F401  (register tasks)
