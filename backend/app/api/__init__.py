from fastapi import APIRouter
from app.api.auth import router as auth_router
from app.api.datasets import router as datasets_router
from app.api.models import router as models_router
from app.api.inference import router as inference_router
from app.api.distribution import router as distribution_router
from app.api.simulator import router as simulator_router
from app.api.assurance import router as assurance_router
from app.api.audit import router as audit_router
from app.api.assets import router as assets_router
from app.api.reports import router as reports_router
from app.api.system import router as system_router

api_router = APIRouter()

api_router.include_router(auth_router)
api_router.include_router(datasets_router)
api_router.include_router(models_router)
api_router.include_router(inference_router)
api_router.include_router(distribution_router)
api_router.include_router(simulator_router)
api_router.include_router(assurance_router)
api_router.include_router(audit_router)
api_router.include_router(assets_router)
api_router.include_router(reports_router)
api_router.include_router(system_router)
