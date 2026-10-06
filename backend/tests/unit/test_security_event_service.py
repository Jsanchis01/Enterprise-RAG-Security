from app.services.security_event_service import SecurityEventService


def test_record_security_event(db):
    event = SecurityEventService.record_event(
        db,
        event_type="DIRECT_PROMPT_INJECTION",
        severity="HIGH",
        pipeline_mode="policy_aware",
        trigger_payload="Ignore previous instructions",
        detection_mechanism="rule_based_input_validation",
        mitigation_action="QUERY_BLOCKED",
        details={
            "rule": "instruction_override",
            "category": "direct_prompt_injection",
        },
    )

    db.commit()

    assert event.id is not None
    assert event.event_type == "DIRECT_PROMPT_INJECTION"
    assert event.severity == "HIGH"
    assert event.pipeline_mode == "policy_aware"
    assert event.detection_mechanism == "rule_based_input_validation"
    assert event.mitigation_action == "QUERY_BLOCKED"
    assert event.details["rule"] == "instruction_override"


def test_record_security_event_with_user(db, test_admin_user):
    event = SecurityEventService.record_event(
        db,
        event_type="UNAUTHORIZED_ACCESS",
        severity="HIGH",
        pipeline_mode="policy_aware",
        trigger_payload="Restricted document retrieval",
        detection_mechanism="metadata_policy_filter",
        mitigation_action="DOCUMENT_FILTERED",
        user_id=test_admin_user.id,
    )

    db.commit()

    assert event.user_id == test_admin_user.id