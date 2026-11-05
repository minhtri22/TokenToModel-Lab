"""F0-only source admission stub. No F1/F2/TEST/corpus access permitted."""
from __future__ import annotations


class SourceNotAdmitted(PermissionError):
    pass


def require_source_scope(*, source: str, admission: str) -> None:
    if source != "F0_SYNTHETIC" or admission != "QA0_F0_SYNTHETIC_ONLY":
        raise SourceNotAdmitted("SOURCE_SCOPE_NOT_APPROVED")


def require_real_corpus(*_args: object, **_kwargs: object) -> None:
    raise SourceNotAdmitted("F1_F2_AND_SCIENTIFIC_TEST_NOT_APPROVED")
