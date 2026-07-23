import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.base import get_db
from app.models.company import Company
from app.models.user import User
from app.models.enums import RoleEnum
from app.core.security import hash_password, verify_password, create_access_token, create_refresh_token, decode_token
from app.schemas.auth import CompanyRegister, LoginRequest, LoginResponse, TokenResponse, UserOut

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register-company", response_model=LoginResponse, status_code=status.HTTP_201_CREATED)
def register_company(payload: CompanyRegister, db: Session = Depends(get_db)):
    existing = db.query(Company).filter(Company.slug == payload.company_slug).first()
    if existing:
        raise HTTPException(status_code=400, detail="Company slug already taken")

    company = Company(id=uuid.uuid4(), name=payload.company_name, slug=payload.company_slug)
    db.add(company)
    db.flush()

    admin = User(
        id=uuid.uuid4(),
        company_id=company.id,
        employee_code="ADMIN-001",
        full_name=payload.admin_full_name,
        email=payload.admin_email,
        hashed_password=hash_password(payload.admin_password),
        role=RoleEnum.ADMIN,
    )
    db.add(admin)
    db.commit()
    db.refresh(admin)

    return _build_login_response(admin)


@router.post("/login", response_model=LoginResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    company = db.query(Company).filter(Company.slug == payload.company_slug, Company.is_active.is_(True)).first()
    if not company:
        raise HTTPException(status_code=401, detail="Invalid company, email, or password")

    user = db.query(User).filter(User.company_id == company.id, User.email == payload.email).first()
    if not user or not user.is_active or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid company, email, or password")

    return _build_login_response(user)


@router.post("/refresh", response_model=TokenResponse)
def refresh(refresh_token: str, db: Session = Depends(get_db)):
    payload = decode_token(refresh_token)
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    user = db.query(User).filter(User.id == payload.get("sub"), User.company_id == payload.get("company_id")).first()
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    claims = {"sub": str(user.id), "company_id": str(user.company_id), "role": user.role.value}
    return TokenResponse(access_token=create_access_token(claims), refresh_token=create_refresh_token(claims))


def _build_login_response(user: User) -> LoginResponse:
    claims = {"sub": str(user.id), "company_id": str(user.company_id), "role": user.role.value}
    tokens = TokenResponse(access_token=create_access_token(claims), refresh_token=create_refresh_token(claims))
    return LoginResponse(tokens=tokens, user=UserOut.model_validate(user))
