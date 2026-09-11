from datetime import datetime, timezone
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import (
    hash_password, verify_password, create_access_token, get_current_user,
    ROLE_ADMIN, ROLE_AUDITOR, ROLE_MODEL_TRAINER, ROLE_DATA_CONTRIBUTOR
)
import uuid
from app.models.orm_models import User, Contributor
from app.schemas.pydantic_schemas import (
    LoginRequest, RegisterRequest, TokenResponse, UserResponse, ContributorCreate, ContributorResponse
)
from app.provenance.ledger import append_block

router = APIRouter(prefix="", tags=["Authentication & Contributors"])

# Default seeded credentials
SEEDED_USERS = {
    "admin": ("admin123", ROLE_ADMIN),
    "auditor": ("auditor123", ROLE_AUDITOR),
    "trainer": ("trainer123", ROLE_MODEL_TRAINER),
    "contributor": ("contrib123", ROLE_DATA_CONTRIBUTOR)
}

@router.post("/auth/login", response_model=TokenResponse)
def login(req: LoginRequest, db: Session = Depends(get_db)):
    """
    Authenticate user locally in offline environment.
    """
    username = req.username.lower().strip()
    user = db.query(User).filter(User.username == username).first()

    # Fallback to seeded demo user accounts if database not seeded yet
    if not user and username in SEEDED_USERS:
        pwd, role = SEEDED_USERS[username]
        if req.password == pwd:
            token = create_access_token({"sub": username, "username": username, "role": role})
            return TokenResponse(access_token=token, role=role, username=username)

    if not user or not verify_password(req.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials. Use demo accounts: admin/admin123, auditor/auditor123, trainer/trainer123, contributor/contrib123"
        )

    token = create_access_token({"sub": user.username, "username": user.username, "role": user.role})
    return TokenResponse(access_token=token, role=user.role, username=user.username)

@router.post("/auth/register", response_model=TokenResponse)
@router.post("/auth/signup", response_model=TokenResponse)
def register(req: RegisterRequest, db: Session = Depends(get_db)):
    """
    Register a new operator or contributor locally in offline SQLite.
    """
    username = req.username.lower().strip()
    if len(username) < 3:
        raise HTTPException(status_code=400, detail="Username must be at least 3 characters long.")
    if len(req.password) < 4:
        raise HTTPException(status_code=400, detail="Password must be at least 4 characters long.")

    existing = db.query(User).filter(User.username == username).first()
    if existing:
        raise HTTPException(status_code=400, detail="Username already registered. Please sign in or use another username.")

    valid_roles = [ROLE_ADMIN, ROLE_AUDITOR, ROLE_MODEL_TRAINER, ROLE_DATA_CONTRIBUTOR]
    chosen_role = req.role.upper().strip()
    if chosen_role not in valid_roles:
        chosen_role = ROLE_DATA_CONTRIBUTOR

    hashed_pw = hash_password(req.password)
    user = User(
        username=username,
        hashed_password=hashed_pw,
        role=chosen_role
    )
    db.add(user)

    contrib_id = f"CONTRIB-{username.upper()}-{uuid.uuid4().hex[:4].upper()}"
    contributor = Contributor(
        contributor_id=contrib_id,
        name=req.name or req.username.capitalize(),
        role=chosen_role,
        organization=req.organization or "Defense Operations Unit",
        trust_score=95.0,
        total_contributions=0,
        flagged_contributions=0,
        risk_indicator="LOW"
    )
    db.add(contributor)
    db.commit()
    db.refresh(user)

    # Commit event to immutable audit ledger
    append_block(
        event_type="OPERATOR_REGISTERED",
        entity_type="USER",
        entity_id=username,
        payload={"username": username, "role": chosen_role, "organization": req.organization},
        operator_id="ADMIN"
    )

    token = create_access_token({"sub": user.username, "username": user.username, "role": user.role})
    return TokenResponse(access_token=token, role=user.role, username=user.username)

@router.get("/auth/me", response_model=UserResponse)
def get_me(current_user: dict = Depends(get_current_user)):
    """
    Return currently active operator credentials and permissions.
    """
    return UserResponse(
        id=1,
        username=current_user.get("username", "admin"),
        role=current_user.get("role", ROLE_ADMIN),
        created_at=datetime.now(timezone.utc)
    )

@router.get("/contributors", response_model=List[ContributorResponse])
def list_contributors(db: Session = Depends(get_db)):
    """
    List registered pipeline contributors and their current integrity/risk indicators.
    """
    contributors = db.query(Contributor).all()
    if not contributors:
        # Return initial representative contributor roster
        return [
            ContributorResponse(
                id=1,
                contributor_id="CONTRIB-ARMY-01",
                name="Signals Corps Data Team",
                role=ROLE_DATA_CONTRIBUTOR,
                organization="Indian Army DGIS",
                trust_score=98.5,
                total_contributions=12,
                flagged_contributions=0,
                risk_indicator="LOW"
            ),
            ContributorResponse(
                id=2,
                contributor_id="CONTRIB-DRDO-02",
                name="DRDO CV Modeling Lab",
                role=ROLE_MODEL_TRAINER,
                organization="DRDO Center for AI",
                trust_score=95.0,
                total_contributions=8,
                flagged_contributions=0,
                risk_indicator="LOW"
            ),
            ContributorResponse(
                id=3,
                contributor_id="CONTRIB-EXTERNAL-03",
                name="Third-Party Surveillance Vendor",
                role=ROLE_DATA_CONTRIBUTOR,
                organization="AeroSensors Pvt Ltd",
                trust_score=68.0,
                total_contributions=15,
                flagged_contributions=3,
                risk_indicator="MEDIUM"
            )
        ]

    return [
        ContributorResponse(
            id=c.id,
            contributor_id=c.contributor_id,
            name=c.name,
            role=c.role,
            organization=c.organization,
            trust_score=c.trust_score,
            total_contributions=c.total_contributions,
            flagged_contributions=c.flagged_contributions,
            risk_indicator=c.risk_indicator
        )
        for c in contributors
    ]

@router.post("/contributors", response_model=ContributorResponse)
def register_contributor(req: ContributorCreate, db: Session = Depends(get_db)):
    """
    Register a new pipeline contributor into the governance registry.
    """
    existing = db.query(Contributor).filter(Contributor.contributor_id == req.contributor_id).first()
    if existing:
        raise HTTPException(status_code=400, detail="Contributor ID already registered")

    contrib = Contributor(
        contributor_id=req.contributor_id,
        name=req.name,
        role=req.role,
        organization=req.organization,
        trust_score=100.0,
        total_contributions=0,
        flagged_contributions=0,
        risk_indicator="LOW"
    )
    db.add(contrib)
    db.commit()
    db.refresh(contrib)

    # Commit event to immutable audit ledger
    append_block(
        event_type="CONTRIBUTOR_REGISTERED",
        entity_type="CONTRIBUTOR",
        entity_id=contrib.contributor_id,
        payload={"name": contrib.name, "role": contrib.role, "org": contrib.organization},
        operator_id="ADMIN"
    )

    return ContributorResponse(
        id=contrib.id,
        contributor_id=contrib.contributor_id,
        name=contrib.name,
        role=contrib.role,
        organization=contrib.organization,
        trust_score=contrib.trust_score,
        total_contributions=contrib.total_contributions,
        flagged_contributions=contrib.flagged_contributions,
        risk_indicator=contrib.risk_indicator
    )
