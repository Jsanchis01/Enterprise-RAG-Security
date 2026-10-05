"""
input_security_service.py – Phase 5: Input Security / Direct Prompt-Injection Detection

Rule-based detector for direct prompt-injection patterns in user queries.

IMPORTANT SCOPE NOTE:
This is an explicitly rule-based, pattern-matching detector designed for controlled
research experimentation scenarios.  It is NOT a complete or production-grade prompt-
injection prevention system.  Its purpose is to demonstrate and measure the impact of
input-security controls in the experimental pipeline comparison.

Design:
- Each rule has a name, severity, and list of compiled regex patterns.
- The first matching rule wins; detection is not exhaustive.
- Returns a structured InputValidationResult rather than raising exceptions.
- No security events are persisted here (Phase 6 responsibility).
- Query text is never logged in full; only rule name and category are recorded.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import List, Optional


# ---------------------------------------------------------------------------
# Severity levels
# ---------------------------------------------------------------------------

class Severity:
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


# ---------------------------------------------------------------------------
# Rule definitions
# ---------------------------------------------------------------------------

@dataclass
class InjectionRule:
    name: str
    category: str
    severity: str
    patterns: List[re.Pattern]


def _compile(patterns: List[str]) -> List[re.Pattern]:
    return [re.compile(p, re.IGNORECASE | re.DOTALL) for p in patterns]


# Ordered from most-specific to most-general
INJECTION_RULES: List[InjectionRule] = [
    InjectionRule(
        name="instruction_override",
        category="direct_prompt_injection",
        severity=Severity.HIGH,
        patterns=_compile([
            r"ignore\s+(all\s+)?previous\s+instructions",
            r"disregard\s+(all\s+)?previous\s+instructions",
            r"forget\s+(your\s+)?(previous\s+)?instructions",
            r"override\s+(all\s+)?instructions",
            r"do\s+not\s+follow\s+(your\s+)?instructions",
            r"new\s+instructions\s*:",
            r"your\s+(new\s+)?instructions\s+(are|now)",
        ]),
    ),
    InjectionRule(
        name="system_prompt_exfiltration",
        category="direct_prompt_injection",
        severity=Severity.HIGH,
        patterns=_compile([
            r"reveal\s+(the\s+)?(system|hidden|original)\s+prompt",
            r"show\s+(me\s+)?(your\s+)?(system\s+message|system\s+prompt|hidden\s+prompt)",
            r"print\s+(your\s+)?system\s+(prompt|message)",
            r"repeat\s+(your\s+)?system\s+prompt",
            r"what\s+(is|are)\s+your\s+system\s+(prompt|instructions)",
            r"display\s+your\s+(initial\s+)?instructions",
        ]),
    ),
    InjectionRule(
        name="policy_bypass",
        category="direct_prompt_injection",
        severity=Severity.HIGH,
        patterns=_compile([
            r"bypass\s+(security|policy|authorization|access\s+control)",
            r"ignore\s+(security|policy|access\s+control|authorization)",
            r"skip\s+(security|policy|authorization|access\s+control)",
            r"disable\s+(security|policy|authorization|filter)",
            r"circumvent\s+(security|policy|authorization)",
        ]),
    ),
    InjectionRule(
        name="role_impersonation",
        category="direct_prompt_injection",
        severity=Severity.HIGH,
        patterns=_compile([
            r"act\s+as\s+(a\s+)?(system|admin|root|developer|superuser)",
            r"pretend\s+(you\s+are|to\s+be)\s+(a\s+)?(system|admin|developer)",
            r"you\s+are\s+now\s+(a\s+)?(system|admin|developer|root)",
            r"switch\s+(to\s+)?(developer|admin|system)\s+mode",
            r"developer\s+mode\s*(enabled|on|active)",
            r"developer\s+message",
            r"jailbreak",
            r"DAN\s+mode",
        ]),
    ),
    InjectionRule(
        name="confidential_disclosure",
        category="direct_prompt_injection",
        severity=Severity.MEDIUM,
        patterns=_compile([
            r"reveal\s+(confidential|restricted|secret|sensitive)\s+(data|information|documents?)",
            r"disclose\s+(confidential|restricted|secret)\s+(data|information)",
            r"send\s+(me\s+)?confidential\s+information",
            r"share\s+(all\s+)?(confidential|restricted)\s+(data|documents?|information)",
            r"output\s+(all\s+)?(confidential|restricted)\s+data",
        ]),
    ),
    InjectionRule(
        name="token_smuggling",
        category="direct_prompt_injection",
        severity=Severity.MEDIUM,
        patterns=_compile([
            r"</?(system|assistant|user|human|ai)\s*>",
            r"\[INST\]",
            r"\[/INST\]",
            r"<\|im_start\|>",
            r"<\|im_end\|>",
            r"<\|system\|>",
        ]),
    ),
]


# ---------------------------------------------------------------------------
# Result dataclass
# ---------------------------------------------------------------------------

@dataclass
class InputValidationResult:
    """
    Result of input security validation on a user query.

    Fields:
        allowed:        True if no injection pattern was detected.
        detected:       True if an injection pattern was matched.
        matched_rule:   Name of the matching rule (None if clean).
        category:       Category of the matched rule (None if clean).
        severity:       Severity level of the matched rule (None if clean).
        reason:         Human-readable explanation for rejection.
    """
    allowed: bool
    detected: bool
    matched_rule: Optional[str] = None
    category: Optional[str] = None
    severity: Optional[str] = None
    reason: str = ""


# ---------------------------------------------------------------------------
# Service
# ---------------------------------------------------------------------------

class InputSecurityService:
    """
    Validates user-supplied query text for direct prompt-injection patterns.

    Usage:
        svc = InputSecurityService()
        result = svc.validate_query(user_query)
        if not result.allowed:
            return error_response(result.reason)
    """

    def __init__(self, rules: Optional[List[InjectionRule]] = None) -> None:
        self._rules = rules if rules is not None else INJECTION_RULES

    def validate_query(self, query: str) -> InputValidationResult:
        """
        Scans the query text against all injection rules.

        Returns InputValidationResult.allowed=True if the query is clean.
        Returns InputValidationResult.allowed=False with matched rule details
        if an injection pattern is detected.

        The query text itself is never included in the result to avoid
        logging sensitive or malicious content unnecessarily.
        """
        if not query or not query.strip():
            return InputValidationResult(
                allowed=False,
                detected=False,
                reason="Query must not be empty.",
            )

        for rule in self._rules:
            for pattern in rule.patterns:
                if pattern.search(query):
                    return InputValidationResult(
                        allowed=False,
                        detected=True,
                        matched_rule=rule.name,
                        category=rule.category,
                        severity=rule.severity,
                        reason=(
                            f"Direct prompt-injection detected: rule='{rule.name}', "
                            f"category='{rule.category}', severity='{rule.severity}'."
                        ),
                    )

        return InputValidationResult(
            allowed=True,
            detected=False,
            reason="Query passed input security validation.",
        )
