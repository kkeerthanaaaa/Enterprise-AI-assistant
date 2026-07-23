import uuid
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.base import get_db
from app.core.deps import get_current_user, require_role, CurrentUser
from app.models.enums import RoleEnum
from app.models.company import Department
from app.schemas.employee import DepartmentCreate, DepartmentOut

router = APIRouter(prefix="/departments", tags=["departments"])


@router.get("", response_model=list[DepartmentOut])
def list_departments(db: Session = Depends(get_db), current_user: CurrentUser = Depends(get_current_user)):
    return db.query(Department).filter(Department.company_id == current_user.company_id).all()


@router.post("", response_model=DepartmentOut, dependencies=[Depends(require_role(RoleEnum.ADMIN))])
def create_department(payload: DepartmentCreate, db: Session = Depends(get_db), current_user: CurrentUser = Depends(get_current_user)):
    dept = Department(id=uuid.uuid4(), company_id=current_user.company_id, name=payload.name, code=payload.code)
    db.add(dept)
    db.commit()
    db.refresh(dept)
    return dept
