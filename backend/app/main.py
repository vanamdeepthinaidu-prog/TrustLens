from contextlib import asynccontextmanager
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings, WORKSPACE_DIR
from app.core.database import engine, Base, SessionLocal
from app.core.security import (
    hash_password, ROLE_ADMIN, ROLE_AUDITOR, ROLE_MODEL_TRAINER, ROLE_DATA_CONTRIBUTOR
)
from app.models.orm_models import User, Contributor
from app.provenance.ledger import get_ledger, append_block
from app.api import api_router

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("visiontrust")

def seed_initial_database():
    """
    Seed initial roles, users, and baseline contributors in offline SQLite environment.
    """
    with SessionLocal() as db:
        # Seed users
        seed_users = [
            ("admin", "admin123", ROLE_ADMIN),
            ("auditor", "auditor123", ROLE_AUDITOR),
            ("trainer", "trainer123", ROLE_MODEL_TRAINER),
            ("contributor", "contrib123", ROLE_DATA_CONTRIBUTOR)
        ]
        for username, raw_pwd, role in seed_users:
            existing = db.query(User).filter(User.username == username).first()
            if not existing:
                u = User(
                    username=username,
                    hashed_password=hash_password(raw_pwd),
                    role=role
                )
                db.add(u)
        db.commit()

        # Seed initial contributors
        if db.query(Contributor).count() == 0:
            c1 = Contributor(
                contributor_id="CONTRIB-ARMY-01",
                name="Signals Corps Data Team",
                role=ROLE_DATA_CONTRIBUTOR,
                organization="Indian Army DGIS",
                trust_score=98.5,
                total_contributions=12,
                flagged_contributions=0,
                risk_indicator="LOW"
            )
            c2 = Contributor(
                contributor_id="CONTRIB-DRDO-02",
                name="DRDO CV Modeling Lab",
                role=ROLE_MODEL_TRAINER,
                organization="DRDO Center for AI",
                trust_score=95.0,
                total_contributions=8,
                flagged_contributions=0,
                risk_indicator="LOW"
            )
            c3 = Contributor(
                contributor_id="CONTRIB-EXTERNAL-03",
                name="Third-Party Surveillance Vendor",
                role=ROLE_DATA_CONTRIBUTOR,
                organization="AeroSensors Pvt Ltd",
                trust_score=68.0,
                total_contributions=15,
                flagged_contributions=3,
                risk_indicator="MEDIUM"
            )
            db.add_all([c1, c2, c3])
            db.commit()

# Ensure tables and seed data are initialized immediately on module load
Base.metadata.create_all(bind=engine)
seed_initial_database()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Startup & shutdown lifecycle management.
    """
    logger.info("Initializing VisionTrust AI Air-Gapped Assurance Platform...")
    Base.metadata.create_all(bind=engine)
    seed_initial_database()
    
    # Initialize tamper-evident audit ledger
    ledger = get_ledger()
    append_block(
        event_type="SYSTEM_BOOT",
        entity_type="SYSTEM",
        entity_id="VISIONTRUST-CORE",
        payload={"mode": "AIR_GAPPED_OFFLINE", "status": "BOOTSTRAP_COMPLETE"},
        operator_id="SYSTEM"
    )
    logger.info("Ledger initialized and system boot recorded successfully.")
    
    yield
    
    logger.info("VisionTrust AI platform shutting down safely.")

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description=settings.DESCRIPTION,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS for React dashboard and local clients
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount all unified API endpoints under /api
app.include_router(api_router, prefix=settings.API_PREFIX)

frontend_dist = WORKSPACE_DIR / "frontend" / "dist"
if frontend_dist.exists():
    from fastapi.staticfiles import StaticFiles
    from fastapi.responses import FileResponse

    assets_dir = frontend_dist / "assets"
    if assets_dir.exists():
        app.mount("/assets", StaticFiles(directory=str(assets_dir)), name="frontend-assets")
    app.mount("/app", StaticFiles(directory=str(frontend_dist), html=True), name="frontend-app")

    @app.get("/favicon.svg")
    def get_favicon():
        fav = frontend_dist / "favicon.svg"
        if fav.exists():
            return FileResponse(str(fav))
        raise HTTPException(status_code=404, detail="Favicon not found")

    @app.get("/icons.svg")
    def get_icons():
        ic = frontend_dist / "icons.svg"
        if ic.exists():
            return FileResponse(str(ic))
        raise HTTPException(status_code=404, detail="Icons not found")

    @app.get("/{full_path:path}")
    def serve_frontend_spa(full_path: str):
        # Do not intercept API, documentation, or OpenAPI schema routes
        if full_path.startswith("api") or full_path.startswith("docs") or full_path.startswith("redoc") or full_path.startswith("openapi.json"):
            raise HTTPException(status_code=404, detail="Endpoint not found")

        # Check for direct static file request from dist
        direct_file = frontend_dist / full_path
        if full_path and direct_file.is_file():
            return FileResponse(str(direct_file))

        # Default fallback to index.html for client-side HTML5 history routing
        index_file = frontend_dist / "index.html"
        if index_file.exists():
            return FileResponse(str(index_file))
        return {
            "platform": settings.PROJECT_NAME,
            "tagline": "Evidence-based integrity assurance for computer vision pipelines.",
            "mode": "Air-Gapped / Offline",
            "documentation": "/docs",
            "status_check": f"{settings.API_PREFIX}/system/status"
        }
else:
    @app.get("/")
    def root():
        return {
            "platform": settings.PROJECT_NAME,
            "tagline": "Evidence-based integrity assurance for computer vision pipelines.",
            "mode": "Air-Gapped / Offline",
            "documentation": "/docs",
            "status_check": f"{settings.API_PREFIX}/system/status"
        }
