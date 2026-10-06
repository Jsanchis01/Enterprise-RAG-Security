from app.models.audit_log import AuditLog
from app.services.audit_service import AuditService, GENESIS_HASH


def create_log(db, query: str):
    return AuditService.create_audit_log(
        db,
        user_id=None,
        role="analyst",
        clearance_level=3,
        pipeline_mode="policy_aware",
        query_text=query,
        retrieved_chunk_ids=["chunk-1"],
        filtered_chunk_ids=["chunk-1"],
        policy_decision="ALLOW",
        response_text="Test response",
        latency_ms=100.0,
        event_type="STANDARD_QUERY",
    )


def test_first_audit_log_uses_genesis_hash(db):
    log = create_log(db, "First query")
    db.commit()

    assert log.prev_log_hash == GENESIS_HASH
    assert len(log.log_hash) == 64
    assert AuditService.verify_log(log) is True


def test_multiple_logs_form_valid_chain(db):
    log1 = create_log(db, "First query")
    db.commit()

    log2 = create_log(db, "Second query")
    db.commit()

    log3 = create_log(db, "Third query")
    db.commit()

    assert log1.prev_log_hash == GENESIS_HASH
    assert log2.prev_log_hash == log1.log_hash
    assert log3.prev_log_hash == log2.log_hash

    valid, errors = AuditService.verify_chain(db)

    assert valid is True
    assert errors == []


def test_tampering_with_middle_record_breaks_chain(db):
    log1 = create_log(db, "First query")
    db.commit()

    log2 = create_log(db, "Second query")
    db.commit()

    log3 = create_log(db, "Third query")
    db.commit()

    assert AuditService.verify_chain(db)[0] is True

    # Simulate database tampering.
    log2.response_text = "Tampered response"
    db.commit()

    valid, errors = AuditService.verify_chain(db)

    assert valid is False
    assert any("Record 2" in error for error in errors)
    assert any("Record 3" in error for error in errors)


def test_tampering_with_previous_hash_is_detected(db):
    log1 = create_log(db, "First query")
    db.commit()

    log2 = create_log(db, "Second query")
    db.commit()

    assert AuditService.verify_chain(db)[0] is True

    log2.prev_log_hash = "a" * 64
    db.commit()

    valid, errors = AuditService.verify_chain(db)

    assert valid is False
    assert any("Record 2" in error for error in errors)