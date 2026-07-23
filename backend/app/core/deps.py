import uuid
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.db.base import get_db
from app.core.security import decode_token
from app.models.user import User
from app.models.enums import RoleEnum, ROLE_LEVEL

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


class CurrentUser:
    """Lightweight auth context attached to every request. Carries company_id
    so every downstream service call is forced to scope by tenant."""

    def __init__(self, user: User):
        self.id: uuid.UUID = user.id
        self.company_id: uuid.UUID = user.company_id
        self.department_id: uuid.UUID | None = user.department_id
        self.role: RoleEnum = user.role
        self.email: str = user.email
        self.full_name: str = user.full_name


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> CurrentUser:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    payload = decode_token(token)
    if payload is None or payload.get("type") != "access":
        raise credentials_exception

    user_id = payload.get("sub")
    company_id = payload.get("company_id")
    if not user_id or not company_id:
        raise credentials_exception

    user = db.query(User).filter(User.id == user_id, User.company_id == company_id).first()
    if user is None or not user.is_active:
        raise credentials_exception

    return CurrentUser(user)


def require_role(minimum_role: RoleEnum):
    """Dependency factory enforcing role hierarchy, e.g. require_role(RoleEnum.HR)
    allows HR and ADMIN, blocks EMPLOYEE and MANAGER."""

    def checker(current_user: CurrentUser = Depends(get_current_user)) -> CurrentUser:
        if ROLE_LEVEL[current_user.role] < ROLE_LEVEL[minimum_role]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Requires {minimum_role.value} role or higher",
            )
        return current_user

    return checker


def assert_same_company(current_user: CurrentUser, resource_company_id: uuid.UUID):
    """Hard tenant-isolation guard. Call this before returning/mutating ANY
    resource that has a company_id column. Never trust a path/query param
    company_id from the client -- always compare against the JWT's."""
    if str(current_user.company_id) != str(resource_company_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resource not found")
