"""Run with: python -m app.db.init_db

Creates the pgvector extension, all tables, and seeds two demo companies
(to make multi-tenant isolation visible/testable immediately) with a small
org chart, leave balances, and sample training records.
"""
import uuid
from datetime import date, timedelta

from sqlalchemy import text

from app.db.base import Base, engine, SessionLocal
from app.core.security import hash_password
from app.models.company import Company, Department
from app.models.user import User
from app.models.leave import LeaveBalance
from app.models.training import Training
from app.models.enums import RoleEnum, LeaveType
import app.models  # noqa: F401  ensures all models are registered on Base


def create_extension_and_tables():
    with engine.connect() as conn:
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        conn.commit()
    Base.metadata.create_all(bind=engine)


def seed_demo_company(db, name: str, slug: str) -> Company:
    company = Company(id=uuid.uuid4(), name=name, slug=slug)
    db.add(company)
    db.flush()

    eng_dept = Department(id=uuid.uuid4(), company_id=company.id, name="Engineering", code="ENG")
    hr_dept = Department(id=uuid.uuid4(), company_id=company.id, name="Human Resources", code="HR")
    db.add_all([eng_dept, hr_dept])
    db.flush()

    admin = User(
        id=uuid.uuid4(), company_id=company.id, employee_code="ADMIN-001",
        full_name="Alex Admin", email=f"admin@{slug}.com",
        hashed_password=hash_password("Password123!"), role=RoleEnum.ADMIN,
        department_id=hr_dept.id, date_joined=date(2020, 1, 1), notice_period_days=60,
    )
    hr_user = User(
        id=uuid.uuid4(), company_id=company.id, employee_code="HR-001",
        full_name="Hannah HR", email=f"hr@{slug}.com",
        hashed_password=hash_password("Password123!"), role=RoleEnum.HR,
        department_id=hr_dept.id, date_joined=date(2021, 3, 1), notice_period_days=45,
    )
    manager = User(
        id=uuid.uuid4(), company_id=company.id, employee_code="MGR-001",
        full_name="Manny Manager", email=f"manager@{slug}.com",
        hashed_password=hash_password("Password123!"), role=RoleEnum.MANAGER,
        department_id=eng_dept.id, date_joined=date(2021, 6, 1), notice_period_days=30,
    )
    db.add_all([admin, hr_user, manager])
    db.flush()

    employee = User(
        id=uuid.uuid4(), company_id=company.id, employee_code="EMP-001",
        full_name="John Employee", email=f"john@{slug}.com",
        hashed_password=hash_password("Password123!"), role=RoleEnum.EMPLOYEE,
        department_id=eng_dept.id, manager_id=manager.id,
        designation="Software Engineer",
        date_joined=date.today() - timedelta(days=60),
        probation_end_date=date.today() + timedelta(days=30),
        notice_period_days=30,
    )
    db.add(employee)
    db.flush()

    year = date.today().year
    for user in (admin, hr_user, manager, employee):
        db.add(LeaveBalance(id=uuid.uuid4(), company_id=company.id, user_id=user.id, leave_type=LeaveType.ANNUAL, year=year, entitled_days=18, used_days=10))
        db.add(LeaveBalance(id=uuid.uuid4(), company_id=company.id, user_id=user.id, leave_type=LeaveType.SICK, year=year, entitled_days=10, used_days=2))
        db.add(LeaveBalance(id=uuid.uuid4(), company_id=company.id, user_id=user.id, leave_type=LeaveType.WFH, year=year, entitled_days=24, used_days=5))

    db.add(Training(id=uuid.uuid4(), company_id=company.id, user_id=employee.id, training_name="Cybersecurity Awareness", is_mandatory=True, completed=False, due_date=date.today() + timedelta(days=14)))

    db.commit()
    return company


def main():
    print("Creating pgvector extension and tables...")
    create_extension_and_tables()

    db = SessionLocal()
    try:
        if db.query(Company).count() == 0:
            print("Seeding demo companies...")
            seed_demo_company(db, "Acme Corp", "acme")
            seed_demo_company(db, "Globex Inc", "globex")
            print("Done. Demo logins (password: Password123!):")
            print("  acme:   admin@acme.com / hr@acme.com / manager@acme.com / john@acme.com")
            print("  globex: admin@globex.com / hr@globex.com / manager@globex.com / john@globex.com")
        else:
            print("Companies already exist, skipping seed.")
    finally:
        db.close()


if __name__ == "__main__":
    main()
