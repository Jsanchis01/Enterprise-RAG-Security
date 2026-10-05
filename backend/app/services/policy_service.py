"""
policy_service.py – Phase 4: Deterministic Policy Engine

Evaluates the authenticated user's actual role, department, and clearance level
against active Policy rows to produce a PolicyDecision that includes a Qdrant
Filter restricting retrieval to the authorised document scope.

Design principles:
- Authorization is always based on the authenticated DB User object.
- Client-supplied role/clearance values are NEVER used.
- Default effect is DENY (no policy → no access).
- Policies are evaluated in priority DESC order; first matching ALLOW wins.
- The generated Qdrant Filter enforces all approved metadata axes.
"""

from __future__ import annotations

from typing import List, Optional
from dataclasses import dataclass, field

from sqlalchemy.orm import Session
from qdrant_client.http.models import (
    Filter,
    FieldCondition,
    MatchAny,
    Range,
)

from app.models.policy import Policy
from app.models.user import User


# ---------------------------------------------------------------------------
# Result dataclass
# ---------------------------------------------------------------------------

@dataclass
class PolicyDecision:
    """
    Result of evaluating a user against the active policy set.

    Fields:
        allowed:            True if at least one matching ALLOW policy was found.
        matched_policy_id:  Primary key of the winning policy (None on deny).
        matched_policy_name: Human-readable policy name (None on deny).
        reason:             Short explanation of the decision.
        qdrant_filter:      Qdrant Filter to apply to retrieval (None on deny).
        effective_clearance: The clearance ceiling applied (None on deny).
        allowed_departments: Departments included in the filter (None on deny).
        allowed_classifications: Classifications included in the filter (None on deny).
        required_trust_statuses: Trust statuses required by the policy (None on deny).
    """
    allowed: bool
    matched_policy_id: Optional[object] = None
    matched_policy_name: Optional[str] = None
    reason: str = ""
    qdrant_filter: Optional[Filter] = None
    effective_clearance: Optional[int] = None
    allowed_departments: Optional[List[str]] = field(default=None)
    allowed_classifications: Optional[List[str]] = field(default=None)
    required_trust_statuses: Optional[List[str]] = field(default=None)


# ---------------------------------------------------------------------------
# Policy engine
# ---------------------------------------------------------------------------

class PolicyService:
    """
    Deterministic, database-backed policy engine.

    Usage (synchronous – matching the existing service architecture):

        service = PolicyService(db)
        decision = service.evaluate(user)
        if not decision.allowed:
            raise PermissionError(decision.reason)
        chunks = retrieval_service.retrieve_chunks(
            query=query, top_k=top_k, query_filter=decision.qdrant_filter
        )
    """

    def __init__(self, db: Session) -> None:
        self._db = db

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def evaluate(self, user: User) -> PolicyDecision:
        """
        Evaluate the authenticated user against the active policy set.

        Policies are loaded ordered by priority DESC so the highest-priority
        policy is checked first.  The first matching ALLOW policy wins.
        If no ALLOW policy matches, returns a DENY decision.

        NOTE: `user` must be a SQLAlchemy User instance loaded from the
        database by the authentication dependency.  Never accept role or
        clearance values from a client request body.
        """
        policies: List[Policy] = (
            self._db.query(Policy)
            .filter(Policy.is_active.is_(True))
            .order_by(Policy.priority.desc())
            .all()
        )

        for policy in policies:
            if self._matches(policy, user):
                if policy.effect.upper() == "DENY":
                    return PolicyDecision(
                        allowed=False,
                        matched_policy_id=policy.id,
                        matched_policy_name=policy.name,
                        reason=(
                            f"Explicitly denied by policy '{policy.name}' "
                            f"(priority={policy.priority})."
                        ),
                    )
                # ALLOW branch – build the Qdrant filter
                effective_clearance = min(
                    user.clearance_level, policy.max_clearance_level
                )
                qdrant_filter = self._build_filter(
                    allowed_departments=policy.allowed_departments,
                    allowed_classifications=policy.allowed_classifications,
                    required_trust_statuses=policy.required_trust_statuses,
                    max_clearance=effective_clearance,
                )
                return PolicyDecision(
                    allowed=True,
                    matched_policy_id=policy.id,
                    matched_policy_name=policy.name,
                    reason=(
                        f"Access granted by policy '{policy.name}' "
                        f"(priority={policy.priority})."
                    ),
                    qdrant_filter=qdrant_filter,
                    effective_clearance=effective_clearance,
                    allowed_departments=list(policy.allowed_departments),
                    allowed_classifications=list(policy.allowed_classifications),
                    required_trust_statuses=list(policy.required_trust_statuses),
                )

        # Default deny – no policy matched
        return PolicyDecision(
            allowed=False,
            reason=(
                f"Access denied: no matching ALLOW policy for role='{user.role}', "
                f"department='{user.department}', clearance={user.clearance_level}."
            ),
        )

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _matches(policy: Policy, user: User) -> bool:
        """
        Returns True if the policy applies to the given user.

        Subject constraints:
          - subject_role: if set, must equal user.role (case-insensitive)
          - subject_department: if set, must equal user.department (case-insensitive)
          - max_clearance_level: user's clearance must be <= policy ceiling
            (a policy with max_clearance_level=0 never matches any user)
        """
        # Role constraint (None / empty string means "any role")
        if policy.subject_role:
            if user.role.lower() != policy.subject_role.lower():
                return False

        # Department constraint (None / empty string means "any department")
        if policy.subject_department:
            if user.department.lower() != policy.subject_department.lower():
                return False

        # Clearance ceiling – user must not exceed policy maximum
        if user.clearance_level > policy.max_clearance_level:
            return False

        return True

    @staticmethod
    def _build_filter(
        allowed_departments: List[str],
        allowed_classifications: List[str],
        required_trust_statuses: List[str],
        max_clearance: int,
    ) -> Filter:
        """
        Constructs a Qdrant boolean Filter that enforces:
          - department IN allowed_departments
          - classification IN allowed_classifications
          - trust_status IN required_trust_statuses
          - clearance_level <= max_clearance  (integer range)
        """
        conditions = []

        if allowed_departments:
            conditions.append(
                FieldCondition(
                    key="department",
                    match=MatchAny(any=allowed_departments),
                )
            )

        if allowed_classifications:
            conditions.append(
                FieldCondition(
                    key="classification",
                    match=MatchAny(any=allowed_classifications),
                )
            )

        if required_trust_statuses:
            conditions.append(
                FieldCondition(
                    key="trust_status",
                    match=MatchAny(any=required_trust_statuses),
                )
            )

        # Clearance range: document clearance_level must be <= user's effective ceiling
        conditions.append(
            FieldCondition(
                key="clearance_level",
                range=Range(lte=max_clearance),
            )
        )

        return Filter(must=conditions)
