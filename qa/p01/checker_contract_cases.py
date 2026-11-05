"""F0 C01-C10 and W01-W12 locked design-only cases; NO automatic execution."""
from __future__ import annotations
from dataclasses import dataclass


@dataclass(frozen=True)
class ContractCase:
    case_id: str
    intent: str
    required_outcome: str


CASES = (
    ContractCase("C01", "B0 full byte domain", "EXACT_256_AND_ROUNDTRIP"),
    ContractCase("C02", "F00-F11 strict byte roundtrip", "EXACT_ALL_TWELVE"),
    ContractCase("C03", "invalid UTF-8 and lone surrogate", "REJECT_WITHOUT_REPLACEMENT"),
    ContractCase("C04", "invalid IDs including bool/float/negative", "REJECT_ALL"),
    ContractCase("C05", "tie/overlap/document boundary", "PREPINNED_ORACLE_MATCH"),
    ContractCase("C06", "reproducibility independent runs", "IDENTICAL_SERIALIZED_SHA"),
    ContractCase("C07", "dedup, transitivity, split, leakage", "ZERO_CROSS_SPLIT_COLLISIONS"),
    ContractCase("C08", "source rights and min 30 groups", "DENY_UNAUTHORIZED_OR_TOO_FEW"),
    ContractCase("C09", "Windows job memory/time/disk", "FAIL_CLOSED_ON_ANY_BYPASS"),
    ContractCase("C10", "evidence/hash/provenance", "REJECT_MISSING_OR_FALSIFIED_RECEIPT"),
)
WINDOWS_NEGATIVE = tuple(
    ContractCase(f"W{i:02d}", "Windows guard negative contract - see H05", "BLOCK_OR_INCONCLUSIVE_NOT_PASS")
    for i in range(1, 13)
)
