"""
Initial User & Role Seeding Script
Populates standard enterprise accounts across all roles, clearance tiers, and departments.
"""
import sys
from pathlib import Path

# Add project root and backend to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "backend"))

from app.core.database import SessionLocal
from app.models.user import User, UserRole, ClearanceLevel, Department
from app.core.security import hash_password
from app.services.auth_service import get_user_by_username

SEED_USERS = [
    {
        "username": "admin",
        "email": "admin@enterprise.internal",
        "password": "Admin#Secure2026",
        "role": UserRole.ADMIN.value,
        "clearance_level": ClearanceLevel.RESTRICTED.value,  # Level 4
        "department": Department.ENGINEERING.value,
    },
    {
        "username": "analyst_fin",
        "email": "analyst.finance@enterprise.internal",
        "password": "Analyst#Fin2026",
        "role": UserRole.ANALYST.value,
        "clearance_level": ClearanceLevel.CONFIDENTIAL.value, # Level 3
        "department": Department.FINANCE.value,
    },
    {
        "username": "employee_hr",
        "email": "employee.hr@enterprise.internal",
        "password": "Employee#HR2026",
        "role": UserRole.EMPLOYEE.value,
        "clearance_level": ClearanceLevel.INTERNAL.value,      # Level 2
        "department": Department.HR.value,
    },
    {
        "username": "intern_legal",
        "email": "intern.legal@enterprise.internal",
        "password": "Intern#Legal2026",
        "role": UserRole.INTERN.value,
        "clearance_level": ClearanceLevel.PUBLIC.value,        # Level 1
        "department": Department.LEGAL.value,
    },
]


def seed_users():
    print("=" * 70)
    print(" SEEDING INITIAL ENTERPRISE USER ACCOUNTS")
    print("=" * 70)
    
    db = SessionLocal()
    try:
        for u in SEED_USERS:
            existing = get_user_by_username(db, u["username"])
            if existing:
                print(f"  [SKIP] User '{u['username']}' already exists.")
                continue

            user = User(
                username=u["username"],
                email=u["email"],
                hashed_password=hash_password(u["password"]),
                role=u["role"],
                clearance_level=u["clearance_level"],
                department=u["department"],
                is_active=True,
            )
            db.add(user)
            db.commit()
            print(f"  [CREATED] '{u['username']}' (Role: {u['role']}, Clearance: Level {u['clearance_level']}, Dept: {u['department']})")

        print("\n[SUCCESS] User seeding complete.")
        print("=" * 70)
    finally:
        db.close()


if __name__ == "__main__":
    seed_users()
