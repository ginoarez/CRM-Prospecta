from app.workers.celery_app import celery


@celery.task(name="ping")
def ping() -> str:
    return "pong"
