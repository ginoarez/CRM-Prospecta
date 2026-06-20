from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings

app = FastAPI(title="Prospecta CRM API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in settings.CORS_ORIGINS.split(",")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {"status": "ok"}


from app.api.routers import auth as auth_router
from app.api.routers import leads as leads_router
from app.api.routers import interactions as interactions_router
from app.api.routers import dashboard as dashboard_router
from app.api.routers import geo as geo_router
from app.api.routers import scoring as scoring_router
from app.api.routers import tasks as tasks_router
from app.api.routers import templates as templates_router
from app.api.routers import messaging as messaging_router
from app.api.routers import proposals as proposals_router
from app.api.routers import email as email_router

app.include_router(auth_router.router)
app.include_router(leads_router.router)
app.include_router(interactions_router.router)
app.include_router(dashboard_router.router)
app.include_router(geo_router.router)
app.include_router(scoring_router.router)
app.include_router(tasks_router.router)
app.include_router(templates_router.router)
app.include_router(messaging_router.router)
app.include_router(proposals_router.router)
app.include_router(email_router.router)
