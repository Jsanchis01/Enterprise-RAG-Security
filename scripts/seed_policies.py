"""
seed_policies.py – Phase 4: Deterministic policy seed

Creates four role-based policies:
  1. admin_full_access        – ADMIN: all departments/classifications, clearance 4
  2. analyst_limited_access   – ANALYST: finance+engineering, up to confidential, clearance 3
  3. employee_standard_access – EMPLOYEE: own dept (all), up to internal, clearance 2
  4. intern_public_access     – INTERN: own dept (all), public only, clearance 1

Script is idempotent: repeated runs do NOT create duplicate rows.

Usage:
    python scripts/seed_policies.py
"""

import sys
import os

# Allow running from the project root without installing the package
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from app.core.database import SessionLocal
from app.models.policy import Policy


# ---------------------------------------------------------------------------
# Deterministic policy definitions
# ---------------------------------------------------------------------------

POLICIES = [
    {
        "name": "admin_full_access",
        "subject_role": "admin",
        "subject_department": None,  # any department
        "max_clearance_level": 4,
        "allowed_departments": ["hr", "finance", "engineering", "legal"],
        "allowed_classifications": ["public", "internal", "confidential", "restricted"],
        "required_trust_statuses": ["certified"],
        "effect": "ALLOW",
        "priority": 100,
        "is_active": True,
    },
    {
        "name": "analyst_limited_access",
        "subject_role": "analyst",
        "subject_department": None,  # any department
        "max_clearance_level": 3,
        "allowed_departments": ["finance", "engineering"],
        "allowed_classifications": ["public", "internal", "confidential"],
        "required_trust_statuses": ["certified"],
        "effect": "ALLOW",
        "priority": 80,
        "is_active": True,
    },
    {
        "name": "employee_standard_access",
        "subject_role": "employee",
        "subject_department": None,  # any department – filter enforces via Qdrant
        "max_clearance_level": 2,
        "allowed_departments": ["hr", "finance", "engineering", "legal"],
        "allowed_classifications": ["public", "internal"],
        "required_trust_statuses": ["certified"],
        "effect": "ALLOW",
        "priority": 60,
        "is_active": True,
    },
    {
        "name": "intern_public_access",
        "subject_role": "intern",
        "subject_department": None,  # any department
        "max_clearance_level": 1,
        "allowed_departments": ["hr", "finance", "engineering", "legal"],
        "allowed_classifications": ["public"],
        "required_trust_statuses": ["certified"],
        "effect": "ALLOW",
        "priority": 40,
        "is_active": True,
    },
]


def seed_policies() -> None:
    db = SessionLocal()
    try:
        created = 0
        skipped = 0
        for policy_data in POLICIES:
            existing = (
                db.query(Policy).filter(Policy.name == policy_data["name"]).first()
            )
            if existing is not None:
                skipped += 1
                print(f"  [SKIP]    Policy '{policy_data['name']}' already exists.")
                continue

            policy = Policy(**policy_data)
            db.add(policy)
            created += 1
            print(f"  [CREATE]  Policy '{policy_data['name']}' created.")

        db.commit()
        print(
            f"\nSeeding complete: {created} created, {skipped} skipped. "
            f"Total active policies: {db.query(Policy).filter(Policy.is_active.is_(True)).count()}."
        )
    except Exception as exc:
        db.rollback()
        print(f"ERROR: {exc}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    print("Seeding policies …")
    seed_policies()
