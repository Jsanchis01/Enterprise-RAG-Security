import hashlib
import json
from datetime import datetime, timezone
from typing import Any, Optional
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.audit_log import AuditLog


GENESIS_HASH = "0" * 64


class AuditService:
    """Creates and verifies tamper-evident audit-log records."""

    RESEARCH_FIELDS = (
        "timestamp",
        "user_id",
        "role",
        "clearance_level",
        "pipeline_mode",
        "query_text",
        "retrieved_chunk_ids",
        "filtered_chunk_ids",
        "policy_decision",
        "response_text",
        "latency_ms",
        "event_type",
    )

    @staticmethod
    def _normalize(value: Any) -> Any:
        """Convert values into deterministic JSON-compatible forms."""
        if isinstance(value, UUID):
            return str(value)

        if isinstance(value, datetime):
            return value.astimezone(timezone.utc).isoformat()

        if isinstance(value, dict):
            return {
                str(key): AuditService._normalize(val)
                for key, val in value.items()
            }

        if isinstance(value, (list, tuple)):
            return [AuditService._normalize(item) for item in value]

        return value

    @classmethod
    def _canonical_payload(
        cls,
        *,
        timestamp: datetime,
        user_id: Optional[UUID],
        role: str,
        clearance_level: int,
        pipeline_mode: str,
        query_text: str,
        retrieved_chunk_ids: list[str],
        filtered_chunk_ids: list[str],
        policy_decision: str,
        response_text: str,
        latency_ms: float,
        event_type: str,
        prev_log_hash: str,
    ) -> dict[str, Any]:
        """Build the deterministic payload used for hashing."""
        payload = {
            "timestamp": timestamp,
            "user_id": user_id,
            "role": role,
            "clearance_level": clearance_level,
            "pipeline_mode": pipeline_mode,
            "query_text": query_text,
            "retrieved_chunk_ids": retrieved_chunk_ids,
            "filtered_chunk_ids": filtered_chunk_ids,
            "policy_decision": policy_decision,
            "response_text": response_text,
            "latency_ms": latency_ms,
            "event_type": event_type,
            "prev_log_hash": prev_log_hash,
        }

        return cls._normalize(payload)

    @classmethod
    def calculate_log_hash(
        cls,
        *,
        timestamp: datetime,
        user_id: Optional[UUID],
        role: str,
        clearance_level: int,
        pipeline_mode: str,
        query_text: str,
        retrieved_chunk_ids: list[str],
        filtered_chunk_ids: list[str],
        policy_decision: str,
        response_text: str,
        latency_ms: float,
        event_type: str,
        prev_log_hash: str,
    ) -> str:
        """Calculate the SHA-256 hash for one audit record."""
        payload = cls._canonical_payload(
            timestamp=timestamp,
            user_id=user_id,
            role=role,
            clearance_level=clearance_level,
            pipeline_mode=pipeline_mode,
            query_text=query_text,
            retrieved_chunk_ids=retrieved_chunk_ids,
            filtered_chunk_ids=filtered_chunk_ids,
            policy_decision=policy_decision,
            response_text=response_text,
            latency_ms=latency_ms,
            event_type=event_type,
            prev_log_hash=prev_log_hash,
        )

        canonical_json = json.dumps(
            payload,
            sort_keys=True,
            separators=(",", ":"),
        )

        return hashlib.sha256(
            canonical_json.encode("utf-8")
        ).hexdigest()

    @staticmethod
    def get_previous_hash(db: Session) -> str:
        """Return the latest audit hash, or the genesis hash."""
        latest = (
            db.query(AuditLog)
            .order_by(AuditLog.timestamp.desc(), AuditLog.id.desc())
            .first()
        )

        return latest.log_hash if latest else GENESIS_HASH

    @classmethod
    def create_audit_log(
        cls,
        db: Session,
        *,
        user_id: Optional[UUID],
        role: str,
        clearance_level: int,
        pipeline_mode: str,
        query_text: str,
        retrieved_chunk_ids: list[str],
        filtered_chunk_ids: list[str],
        policy_decision: str,
        response_text: str,
        latency_ms: float,
        event_type: str = "STANDARD_QUERY",
        client_ip: str = "127.0.0.1",
    ) -> AuditLog:
        """Create, hash, and persist one audit record."""
        timestamp = datetime.now(timezone.utc)
        prev_log_hash = cls.get_previous_hash(db)

        log_hash = cls.calculate_log_hash(
            timestamp=timestamp,
            user_id=user_id,
            role=role,
            clearance_level=clearance_level,
            pipeline_mode=pipeline_mode,
            query_text=query_text,
            retrieved_chunk_ids=retrieved_chunk_ids,
            filtered_chunk_ids=filtered_chunk_ids,
            policy_decision=policy_decision,
            response_text=response_text,
            latency_ms=latency_ms,
            event_type=event_type,
            prev_log_hash=prev_log_hash,
        )

        audit_log = AuditLog(
            timestamp=timestamp,
            user_id=user_id,
            role=role,
            clearance_level=clearance_level,
            pipeline_mode=pipeline_mode,
            query_text=query_text,
            retrieved_chunk_ids=retrieved_chunk_ids,
            filtered_chunk_ids=filtered_chunk_ids,
            policy_decision=policy_decision,
            response_text=response_text,
            latency_ms=latency_ms,
            event_type=event_type,
            client_ip=client_ip,
            prev_log_hash=prev_log_hash,
            log_hash=log_hash,
        )

        db.add(audit_log)
        db.flush()

        return audit_log

    @classmethod
    def verify_log(cls, audit_log: AuditLog) -> bool:
        """Verify that one audit record has not been modified."""
        expected_hash = cls.calculate_log_hash(
            timestamp=audit_log.timestamp,
            user_id=audit_log.user_id,
            role=audit_log.role,
            clearance_level=audit_log.clearance_level,
            pipeline_mode=audit_log.pipeline_mode,
            query_text=audit_log.query_text,
            retrieved_chunk_ids=audit_log.retrieved_chunk_ids,
            filtered_chunk_ids=audit_log.filtered_chunk_ids,
            policy_decision=audit_log.policy_decision,
            response_text=audit_log.response_text,
            latency_ms=audit_log.latency_ms,
            event_type=audit_log.event_type,
            prev_log_hash=audit_log.prev_log_hash,
        )

        return expected_hash == audit_log.log_hash

    @classmethod
    def verify_chain(cls, db: Session) -> tuple[bool, list[str]]:
        """
        Verify the complete audit chain.

        Returns:
            (is_valid, errors)
        """
        logs = (
            db.query(AuditLog)
            .order_by(AuditLog.timestamp.asc(), AuditLog.id.asc())
            .all()
        )

        errors: list[str] = []
        expected_previous_hash = GENESIS_HASH

        for index, audit_log in enumerate(logs, start=1):
            if audit_log.prev_log_hash != expected_previous_hash:
                errors.append(
                    f"Record {index}: previous hash mismatch"
                )

            record_valid = cls.verify_log(audit_log)

            if not record_valid:
                errors.append(
                    f"Record {index}: log hash verification failed"
                )

            # Continue the chain using the cryptographically
            # recomputed hash when the current record is tampered.
            if record_valid:
                expected_previous_hash = audit_log.log_hash
            else:
                expected_previous_hash = cls.calculate_log_hash(
                    timestamp=audit_log.timestamp,
                    user_id=audit_log.user_id,
                    role=audit_log.role,
                    clearance_level=audit_log.clearance_level,
                    pipeline_mode=audit_log.pipeline_mode,
                    query_text=audit_log.query_text,
                    retrieved_chunk_ids=audit_log.retrieved_chunk_ids,
                    filtered_chunk_ids=audit_log.filtered_chunk_ids,
                    policy_decision=audit_log.policy_decision,
                    response_text=audit_log.response_text,
                    latency_ms=audit_log.latency_ms,
                    event_type=audit_log.event_type,
                    prev_log_hash=audit_log.prev_log_hash,
                )


        return len(errors) == 0, errors