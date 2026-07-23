import uuid
from pydantic import BaseModel, EmailStr, Field

from app.models.enums import RoleEnum


class CompanyRegister(BaseModel):
    company_name: str = Field(..., min_length=2, max_length=255)
    company_slug: str = Field(..., min_length=2, max_length=100, pattern=r"^[a-z0-9-]+$")
    admin_full_name: str
    admin_email: EmailStr
    admin_password: str = Field(..., min_length=8)


class LoginRequest(BaseModel):
    company_slug: str
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class UserOut(BaseModel):
    id: uuid.UUID
    company_id: uuid.UUID
    full_name: str
    email: EmailStr
    role: RoleEnum
    department_id: uuid.UUID | None = None

    class Config:
        from_attributes = True


class LoginResponse(BaseModel):
    tokens: TokenResponse
    user: UserOut
