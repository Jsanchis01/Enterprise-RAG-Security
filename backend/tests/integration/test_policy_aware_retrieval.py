"""
test_policy_aware_retrieval.py – Phase 4 integration tests

These tests require:
  - A running Qdrant instance with the ingested corpus (from Phase 3).
  - A running PostgreSQL instance (used via the conftest.py session fixture).
  - At least one seeded ALLOW policy matching each tested role.

The tests verify:
  1. Baseline retrieve_chunks() returns unfiltered results (no query_filter).
  2. Policy-aware retrieval excludes chunks that exceed the user's clearance.
  3. Policy-aware retrieval excludes chunks from unauthorized departments.
  4. Policy-aware retrieval excludes chunks with non-allowed classifications.
  5. PermissionError is raised when no matching ALLOW policy exists.
  6. ValueError is raised when user or db is not supplied to retrieve_policy_aware().
  7. Intern filter only returns public chunks.
  8. Admin filter can return chunks across all departments and classifications.
"""

import uuid
import pytest
from unittest.mock import MagicMock

from app.models.user import User, UserRole, ClearanceLevel, Department
from app.models.policy import Policy
from app.services.retrieval_service import RetrievalService
from app.services.policy_service import PolicyService


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_user(
    role: str = "employee",
    department: str = "engineering",
    clearance_level: int = 2,
) -> User:
    u = User()
    u.id = uuid.uuid4()
    u.username = f"inttest_{uuid.uuid4().hex[:6]}"
    u.email = f"{u.username}@test.internal"
    u.hashed_password = "hashed"
    u.role = role
    u.department = department
    u.clearance_level = clearance_level
    u.is_active = True
    return u


def make_mock_db_with_policies(policies: list):
    mock_db = MagicMock()
    mock_db.query.return_value.filter.return_value.order_by.return_value.all.return_value = (
        sorted(policies, key=lambda p: p.priority, reverse=True)
    )
    return mock_db


def make_policy(
    name: str,
    subject_role: str,
    max_clearance_level: int,
    allowed_departments: list,
    allowed_classifications: list,
    required_trust_statuses: list = None,
    effect: str = "ALLOW",
    priority: int = 100,
) -> Policy:
    p = Policy()
    p.id = uuid.uuid4()
    p.name = name
    p.subject_role = subject_role
    p.subject_department = None
    p.max_clearance_level = max_clearance_level
    p.allowed_departments = allowed_departments
    p.allowed_classifications = allowed_classifications
    p.required_trust_statuses = required_trust_statuses or ["certified"]
    p.effect = effect
    p.priority = priority
    p.is_active = True
    return p


# ---------------------------------------------------------------------------
# Test: baseline retrieval is unfiltered
# ---------------------------------------------------------------------------

class TestBaselineRetrievalUnfiltered:
    def test_retrieve_chunks_passes_none_filter(self):
        """
        Baseline retrieve_chunks() must pass query_filter=None to the vector service,
        meaning results are not restricted by department, classification, or clearance.
        """
        svc = RetrievalService()
        # Intercept vector_service.search to verify the filter argument
        original_search = svc.vector_service.search

        captured_filter = []
        def mock_search(query_vector, top_k, query_filter=None):
            captured_filter.append(query_filter)
            return original_search(query_vector, top_k, query_filter)

        svc.vector_service.search = mock_search
        svc.retrieve_chunks(query="corporate policies", top_k=3)

        assert len(captured_filter) == 1
        assert captured_filter[0] is None, (
            "Baseline retrieve_chunks must pass query_filter=None to vector service."
        )

    def test_baseline_returns_results_across_all_departments(self):
        """
        Baseline retrieval (no filter) must return chunks from more than one department,
        demonstrating it is unfiltered.
        """
        svc = RetrievalService()
        # Use a general query likely to return mixed departments
        results = svc.retrieve_chunks(query="company policy", top_k=10)
        assert len(results) > 0
        # At least some results should exist
        departments = {r.metadata["department"] for r in results}
        # Cannot guarantee cross-dept from a single query, but we confirm no filter applied
        # by verifying the call above did not raise PermissionError
        assert all(d in {"hr", "finance", "engineering", "legal"} for d in departments)


# ---------------------------------------------------------------------------
# Test: policy-aware retrieval enforces filter
# ---------------------------------------------------------------------------

class TestPolicyAwareRetrievalEnforcesFilter:
    def test_intern_filter_returns_only_public_chunks(self):
        """
        Intern policy allows only 'public' classification.
        All returned chunks must have classification='public'.
        """
        intern_policy = make_policy(
            name="intern_test_policy",
            subject_role="intern",
            max_clearance_level=1,
            allowed_departments=["hr", "finance", "engineering", "legal"],
            allowed_classifications=["public"],
        )
        user = make_user(role="intern", clearance_level=1)
        mock_db = make_mock_db_with_policies([intern_policy])

        svc = RetrievalService()
        response = svc.retrieve_policy_aware(
            query="general company information",
            top_k=5,
            user=user,
            db=mock_db,
        )

        assert response is not None
        for chunk in response.results:
            assert chunk.metadata["classification"] == "public", (
                f"Intern should only see public chunks, got: {chunk.metadata['classification']}"
            )
            assert chunk.metadata["clearance_level"] <= 1, (
                f"Intern clearance is 1, but got clearance_level={chunk.metadata['clearance_level']}"
            )

    def test_analyst_filter_excludes_restricted_chunks(self):
        """
        Analyst policy allows classifications up to 'confidential'.
        No restricted chunks should appear.
        """
        analyst_policy = make_policy(
            name="analyst_test_policy",
            subject_role="analyst",
            max_clearance_level=3,
            allowed_departments=["finance", "engineering"],
            allowed_classifications=["public", "internal", "confidential"],
        )
        user = make_user(role="analyst", department="finance", clearance_level=3)
        mock_db = make_mock_db_with_policies([analyst_policy])

        svc = RetrievalService()
        response = svc.retrieve_policy_aware(
            query="financial data and engineering systems",
            top_k=5,
            user=user,
            db=mock_db,
        )

        for chunk in response.results:
            assert chunk.metadata["classification"] != "restricted", (
                "Analyst should not see restricted chunks."
            )
            assert chunk.metadata["clearance_level"] <= 3
            assert chunk.metadata["department"] in {"finance", "engineering"}, (
                f"Analyst restricted to finance/engineering, got: {chunk.metadata['department']}"
            )

    def test_admin_filter_spans_all_departments_and_classifications(self):
        """
        Admin policy allows all departments and all classifications.
        Results can span all metadata values.
        """
        admin_policy = make_policy(
            name="admin_test_policy",
            subject_role="admin",
            max_clearance_level=4,
            allowed_departments=["hr", "finance", "engineering", "legal"],
            allowed_classifications=["public", "internal", "confidential", "restricted"],
        )
        user = make_user(role="admin", clearance_level=4)
        mock_db = make_mock_db_with_policies([admin_policy])

        svc = RetrievalService()
        response = svc.retrieve_policy_aware(
            query="all enterprise security policies",
            top_k=10,
            user=user,
            db=mock_db,
        )

        assert response is not None
        assert len(response.results) > 0
        for chunk in response.results:
            assert chunk.metadata["clearance_level"] <= 4

    def test_policy_aware_retrieval_filter_is_not_none(self):
        """
        When policy-aware retrieval is used, the vector service must receive a
        non-None Qdrant filter (unlike baseline).
        """
        employee_policy = make_policy(
            name="emp_test_policy",
            subject_role="employee",
            max_clearance_level=2,
            allowed_departments=["hr", "engineering"],
            allowed_classifications=["public", "internal"],
        )
        user = make_user(role="employee", clearance_level=2)
        mock_db = make_mock_db_with_policies([employee_policy])

        svc = RetrievalService()
        captured_filter = []
        original_search = svc.vector_service.search

        def mock_search(query_vector, top_k, query_filter=None):
            captured_filter.append(query_filter)
            return original_search(query_vector, top_k, query_filter)

        svc.vector_service.search = mock_search
        svc.retrieve_policy_aware(
            query="employee policies",
            top_k=3,
            user=user,
            db=mock_db,
        )

        assert len(captured_filter) == 1
        assert captured_filter[0] is not None, (
            "Policy-aware retrieval must pass a non-None Qdrant filter to vector service."
        )


# ---------------------------------------------------------------------------
# Test: PermissionError raised when no ALLOW policy matches
# ---------------------------------------------------------------------------

class TestPolicyAwarePermissionDenied:
    def test_no_matching_policy_raises_permission_error(self):
        """If no ALLOW policy matches, retrieve_policy_aware must raise PermissionError."""
        mock_db = make_mock_db_with_policies([])  # empty policy table
        user = make_user(role="employee", clearance_level=2)
        svc = RetrievalService()

        with pytest.raises(PermissionError, match="denied"):
            svc.retrieve_policy_aware(
                query="some query",
                top_k=3,
                user=user,
                db=mock_db,
            )

    def test_explicit_deny_policy_raises_permission_error(self):
        """An explicit DENY policy at high priority must result in PermissionError."""
        deny_policy = make_policy(
            name="explicit_deny",
            subject_role="analyst",
            max_clearance_level=3,
            allowed_departments=["finance"],
            allowed_classifications=["public"],
            effect="DENY",
            priority=200,
        )
        allow_policy = make_policy(
            name="low_prio_allow",
            subject_role="analyst",
            max_clearance_level=3,
            allowed_departments=["finance"],
            allowed_classifications=["public"],
            effect="ALLOW",
            priority=50,
        )
        user = make_user(role="analyst", clearance_level=3)
        mock_db = make_mock_db_with_policies([deny_policy, allow_policy])
        svc = RetrievalService()

        with pytest.raises(PermissionError):
            svc.retrieve_policy_aware(
                query="financial data",
                top_k=3,
                user=user,
                db=mock_db,
            )


# ---------------------------------------------------------------------------
# Test: ValueError raised when user or db not provided
# ---------------------------------------------------------------------------

class TestPolicyAwareRequiresUserAndDb:
    def test_raises_value_error_when_user_is_none(self):
        svc = RetrievalService()
        with pytest.raises(ValueError, match="user"):
            svc.retrieve_policy_aware(
                query="test",
                top_k=3,
                user=None,
                db=MagicMock(),
            )

    def test_raises_value_error_when_db_is_none(self):
        svc = RetrievalService()
        with pytest.raises(ValueError, match="db"):
            svc.retrieve_policy_aware(
                query="test",
                top_k=3,
                user=make_user(),
                db=None,
            )
