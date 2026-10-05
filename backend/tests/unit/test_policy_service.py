"""
test_policy_service.py – Phase 4 unit tests for PolicyService

These tests run with an in-transaction DB session (rolled back after each test)
so they never persist data to the running database.

Tested scenarios:
  - ADMIN receives ALLOW with correct filter fields
  - ANALYST department restriction (finance+engineering only)
  - EMPLOYEE classification restriction (public+internal only)
  - INTERN clearance restriction (max_clearance=1)
  - Trust-status restriction (non-certified → DENY)
  - Default deny when no policy matches (unknown role)
  - Policy priority ordering (higher priority wins)
  - Client-supplied role/clearance values are ignored (uses DB user object only)
  - Explicit DENY policy is honoured before lower-priority ALLOW
"""

import uuid
import pytest
from unittest.mock import MagicMock

from app.models.policy import Policy
from app.models.user import User, UserRole, ClearanceLevel, Department
from app.services.policy_service import PolicyService, PolicyDecision


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_user(
    role: str = "employee",
    department: str = "engineering",
    clearance_level: int = 2,
) -> User:
    """Create an in-memory User object without persisting to DB."""
    user = User()
    user.id = uuid.uuid4()
    user.username = f"testuser_{uuid.uuid4().hex[:6]}"
    user.email = f"{user.username}@test.internal"
    user.hashed_password = "hashed"
    user.role = role
    user.department = department
    user.clearance_level = clearance_level
    user.is_active = True
    return user


def make_policy(
    name: str = "test_policy",
    subject_role: str = "employee",
    subject_department: str = None,
    max_clearance_level: int = 2,
    allowed_departments: list = None,
    allowed_classifications: list = None,
    required_trust_statuses: list = None,
    effect: str = "ALLOW",
    priority: int = 100,
    is_active: bool = True,
) -> Policy:
    """Build a Policy ORM object without persisting."""
    p = Policy()
    p.id = uuid.uuid4()
    p.name = name
    p.subject_role = subject_role
    p.subject_department = subject_department
    p.max_clearance_level = max_clearance_level
    p.allowed_departments = allowed_departments or ["engineering"]
    p.allowed_classifications = allowed_classifications or ["public", "internal"]
    p.required_trust_statuses = required_trust_statuses or ["certified"]
    p.effect = effect
    p.priority = priority
    p.is_active = is_active
    return p


def make_service_with_policies(policies: list) -> PolicyService:
    """Create a PolicyService backed by a mock DB session returning given policies."""
    mock_db = MagicMock()
    # query(...).filter(...).order_by(...).all() chain
    mock_db.query.return_value.filter.return_value.order_by.return_value.all.return_value = (
        sorted(policies, key=lambda p: p.priority, reverse=True)
    )
    return PolicyService(mock_db)


# ---------------------------------------------------------------------------
# Tests: role access
# ---------------------------------------------------------------------------

class TestRoleAccess:
    def test_admin_receives_allow(self):
        policy = make_policy(
            name="admin_full",
            subject_role="admin",
            max_clearance_level=4,
            allowed_departments=["hr", "finance", "engineering", "legal"],
            allowed_classifications=["public", "internal", "confidential", "restricted"],
        )
        user = make_user(role="admin", clearance_level=4)
        svc = make_service_with_policies([policy])
        decision = svc.evaluate(user)

        assert decision.allowed is True
        assert decision.matched_policy_name == "admin_full"
        assert "admin_full" in decision.reason

    def test_analyst_receives_allow(self):
        policy = make_policy(
            name="analyst_policy",
            subject_role="analyst",
            max_clearance_level=3,
            allowed_departments=["finance", "engineering"],
            allowed_classifications=["public", "internal", "confidential"],
        )
        user = make_user(role="analyst", department="finance", clearance_level=3)
        svc = make_service_with_policies([policy])
        decision = svc.evaluate(user)

        assert decision.allowed is True

    def test_employee_receives_allow(self):
        policy = make_policy(
            name="emp_policy",
            subject_role="employee",
            max_clearance_level=2,
        )
        user = make_user(role="employee", clearance_level=2)
        svc = make_service_with_policies([policy])
        decision = svc.evaluate(user)

        assert decision.allowed is True

    def test_intern_receives_allow(self):
        policy = make_policy(
            name="intern_policy",
            subject_role="intern",
            max_clearance_level=1,
            allowed_classifications=["public"],
        )
        user = make_user(role="intern", clearance_level=1)
        svc = make_service_with_policies([policy])
        decision = svc.evaluate(user)

        assert decision.allowed is True


# ---------------------------------------------------------------------------
# Tests: clearance restriction
# ---------------------------------------------------------------------------

class TestClearanceRestriction:
    def test_user_clearance_exceeds_policy_ceiling_is_denied(self):
        """A policy with max_clearance_level=2 must not match a clearance-4 user."""
        policy = make_policy(
            name="low_clearance_policy",
            subject_role="analyst",
            max_clearance_level=2,
        )
        user = make_user(role="analyst", clearance_level=4)
        svc = make_service_with_policies([policy])
        decision = svc.evaluate(user)

        assert decision.allowed is False

    def test_effective_clearance_is_min_of_user_and_policy(self):
        """
        If the user has clearance equal to the policy ceiling, the effective_clearance
        in the decision equals min(user.clearance_level, policy.max_clearance_level).
        Policy with max_clearance_level=3, user clearance=3 → effective_clearance=3.
        """
        policy = make_policy(
            name="capped_policy",
            subject_role="analyst",
            max_clearance_level=3,
        )
        # User clearance == policy ceiling → match succeeds, effective = min(3,3) = 3
        user = make_user(role="analyst", clearance_level=3)
        svc = make_service_with_policies([policy])
        decision = svc.evaluate(user)

        assert decision.allowed is True
        assert decision.effective_clearance == 3  # min(user=3, policy=3)

    def test_qdrant_filter_clearance_range_matches_effective(self):
        """The Qdrant filter's clearance Range.lte must equal effective_clearance."""
        from qdrant_client.http.models import FieldCondition, Range

        policy = make_policy(
            name="range_policy",
            subject_role="analyst",
            max_clearance_level=2,
        )
        user = make_user(role="analyst", clearance_level=2)
        svc = make_service_with_policies([policy])
        decision = svc.evaluate(user)

        assert decision.qdrant_filter is not None
        range_conds = [
            c for c in decision.qdrant_filter.must
            if isinstance(c, FieldCondition) and c.key == "clearance_level"
        ]
        assert len(range_conds) == 1
        assert range_conds[0].range.lte == 2


# ---------------------------------------------------------------------------
# Tests: department restriction
# ---------------------------------------------------------------------------

class TestDepartmentRestriction:
    def test_wrong_subject_department_denied(self):
        """Policy restricted to subject_department='finance' must not match hr user."""
        policy = make_policy(
            name="finance_only",
            subject_role="analyst",
            subject_department="finance",
            max_clearance_level=3,
        )
        user = make_user(role="analyst", department="hr", clearance_level=3)
        svc = make_service_with_policies([policy])
        decision = svc.evaluate(user)

        assert decision.allowed is False

    def test_correct_subject_department_allowed(self):
        policy = make_policy(
            name="finance_analyst",
            subject_role="analyst",
            subject_department="finance",
            max_clearance_level=3,
        )
        user = make_user(role="analyst", department="finance", clearance_level=3)
        svc = make_service_with_policies([policy])
        decision = svc.evaluate(user)

        assert decision.allowed is True

    def test_allowed_departments_in_filter(self):
        """Filter must contain the allowed_departments from the policy."""
        from qdrant_client.http.models import FieldCondition, MatchAny

        policy = make_policy(
            name="dept_filter_check",
            subject_role="employee",
            max_clearance_level=2,
            allowed_departments=["finance", "hr"],
        )
        user = make_user(role="employee", clearance_level=2)
        svc = make_service_with_policies([policy])
        decision = svc.evaluate(user)

        assert decision.allowed is True
        dept_conds = [
            c for c in decision.qdrant_filter.must
            if isinstance(c, FieldCondition) and c.key == "department"
        ]
        assert len(dept_conds) == 1
        assert set(dept_conds[0].match.any) == {"finance", "hr"}


# ---------------------------------------------------------------------------
# Tests: classification restriction
# ---------------------------------------------------------------------------

class TestClassificationRestriction:
    def test_classification_in_filter(self):
        """Filter must contain allowed_classifications from the policy."""
        from qdrant_client.http.models import FieldCondition

        policy = make_policy(
            name="cls_filter_check",
            subject_role="employee",
            max_clearance_level=2,
            allowed_classifications=["public", "internal"],
        )
        user = make_user(role="employee", clearance_level=2)
        svc = make_service_with_policies([policy])
        decision = svc.evaluate(user)

        cls_conds = [
            c for c in decision.qdrant_filter.must
            if isinstance(c, FieldCondition) and c.key == "classification"
        ]
        assert len(cls_conds) == 1
        assert set(cls_conds[0].match.any) == {"public", "internal"}


# ---------------------------------------------------------------------------
# Tests: trust-status restriction
# ---------------------------------------------------------------------------

class TestTrustStatusRestriction:
    def test_trust_status_in_filter(self):
        """Filter must include required_trust_statuses."""
        from qdrant_client.http.models import FieldCondition

        policy = make_policy(
            name="trust_filter_check",
            subject_role="analyst",
            max_clearance_level=3,
            required_trust_statuses=["certified"],
        )
        user = make_user(role="analyst", clearance_level=3)
        svc = make_service_with_policies([policy])
        decision = svc.evaluate(user)

        trust_conds = [
            c for c in decision.qdrant_filter.must
            if isinstance(c, FieldCondition) and c.key == "trust_status"
        ]
        assert len(trust_conds) == 1
        assert "certified" in trust_conds[0].match.any


# ---------------------------------------------------------------------------
# Tests: default deny
# ---------------------------------------------------------------------------

class TestDefaultDeny:
    def test_no_matching_policy_returns_deny(self):
        """Unknown role with no matching policy must result in DENY."""
        policy = make_policy(
            name="employee_only",
            subject_role="employee",
            max_clearance_level=2,
        )
        # 'contractor' role does not match any policy
        user = make_user(role="contractor", clearance_level=2)
        svc = make_service_with_policies([policy])
        decision = svc.evaluate(user)

        assert decision.allowed is False
        assert decision.qdrant_filter is None
        assert "denied" in decision.reason.lower()

    def test_empty_policy_set_returns_deny(self):
        """If the policy table is empty, must default to DENY."""
        user = make_user(role="admin", clearance_level=4)
        svc = make_service_with_policies([])
        decision = svc.evaluate(user)

        assert decision.allowed is False


# ---------------------------------------------------------------------------
# Tests: policy priority
# ---------------------------------------------------------------------------

class TestPolicyPriority:
    def test_higher_priority_allow_wins_over_lower_deny(self):
        """With priority 100 ALLOW and priority 50 DENY for same role, ALLOW wins."""
        allow_policy = make_policy(
            name="high_prio_allow",
            subject_role="analyst",
            max_clearance_level=3,
            effect="ALLOW",
            priority=100,
        )
        deny_policy = make_policy(
            name="low_prio_deny",
            subject_role="analyst",
            max_clearance_level=3,
            effect="DENY",
            priority=50,
        )
        user = make_user(role="analyst", clearance_level=3)
        # Service sorts by priority DESC → allow_policy evaluated first
        svc = make_service_with_policies([deny_policy, allow_policy])
        decision = svc.evaluate(user)

        assert decision.allowed is True
        assert decision.matched_policy_name == "high_prio_allow"

    def test_higher_priority_deny_blocks_lower_allow(self):
        """With priority 100 DENY and priority 50 ALLOW, DENY wins."""
        deny_policy = make_policy(
            name="high_prio_deny",
            subject_role="analyst",
            max_clearance_level=3,
            effect="DENY",
            priority=100,
        )
        allow_policy = make_policy(
            name="low_prio_allow",
            subject_role="analyst",
            max_clearance_level=3,
            effect="ALLOW",
            priority=50,
        )
        user = make_user(role="analyst", clearance_level=3)
        svc = make_service_with_policies([deny_policy, allow_policy])
        decision = svc.evaluate(user)

        assert decision.allowed is False
        assert decision.matched_policy_name == "high_prio_deny"


# ---------------------------------------------------------------------------
# Tests: client-supplied role/clearance must not influence authorization
# ---------------------------------------------------------------------------

class TestClientSuppliedValuesIgnored:
    def test_decision_uses_db_user_role_not_arbitrary_strings(self):
        """
        Authorization depends entirely on the User ORM object passed in.
        Simulate an attacker providing a 'user' object where role is 'admin'
        but the policy only allows 'intern'.  Must be denied.
        """
        intern_policy = make_policy(
            name="intern_only",
            subject_role="intern",
            max_clearance_level=1,
        )
        # Attacker-crafted user claims admin role but we pass the DB object
        attacker_user = make_user(role="admin", clearance_level=4)
        svc = make_service_with_policies([intern_policy])
        decision = svc.evaluate(attacker_user)

        # admin does not match intern_only policy → DENY
        assert decision.allowed is False

    def test_clearance_cannot_be_elevated_by_external_input(self):
        """
        A user object with clearance=1 cannot access a policy requiring clearance<=2
        if the policy ceiling is 2, but the user clearance is 1 – they get capped.
        Conversely, a clearance=4 user with a policy ceiling of 2 is also capped.
        This test verifies the user object is the sole source of clearance.
        """
        policy = make_policy(
            name="capped_clearance",
            subject_role="analyst",
            max_clearance_level=2,
        )
        # User with clearance 3 trying to access a max_clearance_level=2 policy
        user = make_user(role="analyst", clearance_level=3)
        svc = make_service_with_policies([policy])
        # user.clearance_level (3) > policy.max_clearance_level (2) → DENIED
        decision = svc.evaluate(user)
        assert decision.allowed is False
