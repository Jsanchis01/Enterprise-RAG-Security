from datetime import datetime, timezone
from uuid import uuid4

from app.services.audit_service import AuditService, GENESIS_HASH


def build_payload():
    return {
        "timestamp": datetime(2026, 10, 6, 12, 0, tzinfo=timezone.utc),
        "user_id": uuid4(),
        "role": "analyst",
        "clearance_level": 3,
        "pipeline_mode": "policy_aware",
        "query_text": "What is the travel allowance?",
        "retrieved_chunk_ids": ["chunk-1", "chunk-2"],
        "filtered_chunk_ids": ["chunk-1"],
        "policy_decision": "ALLOW",
        "response_text": "The travel allowance is $75.",
        "latency_ms": 125.5,
        "event_type": "STANDARD_QUERY",
        "prev_log_hash": GENESIS_HASH,
    }


def calculate(payload):
    return AuditService.calculate_log_hash(**payload)


def test_hash_is_deterministic():
    payload = build_payload()

    hash_1 = calculate(payload)
    hash_2 = calculate(payload)

    assert hash_1 == hash_2
    assert len(hash_1) == 64


def test_hash_changes_when_research_field_changes():
    payload = build_payload()

    original = calculate(payload)

    payload["query_text"] = "Different query"

    modified = calculate(payload)

    assert original != modified


def test_hash_changes_when_previous_hash_changes():
    payload = build_payload()

    original = calculate(payload)

    payload["prev_log_hash"] = "a" * 64

    modified = calculate(payload)

    assert original != modified


def test_genesis_hash_is_64_zeroes():
    assert GENESIS_HASH == "0" * 64


def test_verify_log_detects_tampering():
    from app.models.audit_log import AuditLog

    payload = build_payload()
    log_hash = calculate(payload)

    audit_log = AuditLog(
        timestamp=payload["timestamp"],
        user_id=payload["user_id"],
        role=payload["role"],
        clearance_level=payload["clearance_level"],
        pipeline_mode=payload["pipeline_mode"],
        query_text=payload["query_text"],
        retrieved_chunk_ids=payload["retrieved_chunk_ids"],
        filtered_chunk_ids=payload["filtered_chunk_ids"],
        policy_decision=payload["policy_decision"],
        response_text=payload["response_text"],
        latency_ms=payload["latency_ms"],
        event_type=payload["event_type"],
        prev_log_hash=payload["prev_log_hash"],
        log_hash=log_hash,
    )

    assert AuditService.verify_log(audit_log) is True

    audit_log.response_text = "Tampered response"

    assert AuditService.verify_log(audit_log) is False