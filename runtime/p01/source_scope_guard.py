"""F0-only source admission stub. No F1/F2/TEST/corpus access permitted."""
from __future__ import annotations


class SourceNotAdmitted(PermissionError):
    pass


import hashlib

# Pinned F0-byte identity, NOT a runtime authority token or a filesystem sandbox.
# Only these hand-authored F00-F11 vectors and the M01 "abababab" oracle are
# acceptable at the synthetic QA0 entry points. No real corpus is admitted.
F0_LITERAL_SHA256 = frozenset({
    "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",  # F00
    "52ce7f8d6d1f955e01b896c8fb38de421b4f9d0a2978fb1e3a3c9f3a6efa80ff",  # F01
    "096b1b5c74b5228a3eefceac7aefcc39432b35b7d24ee4885b1dd06d1045dc77",  # F02
    "0d840a58efa73fdc1557f97b80dabbda05d19cdeeb808319a484f6a66afd05dc",  # F03
    "3c94a0388b52318853918f13698b0677f047c0f298aba9732f8f3f637f652084",  # F04
    "257631603b5242f4a3990499e6134ee263935a1d4433329bff06531313ed2e58",  # F05
    "4234f1064f32788dc9487507f9eeecd0cdf7df6bd010fd1dad8026226e222813",  # F06
    "eddf68639913a3cb8331cdfe7f87559e0beccf2c289c0d90ac4d89b3204004f8",  # F07
    "91a681b998555fb475479817b126c94e57e52011fa1842c5d188795a4a05226b",  # F08
    "d53eda7a637c99cc7fb566d96e9fa109bf15c478410a3f5eb4d4c4e26cd081f6",  # F09
    "836203944f4c0280461ad73d31457c22ba19d1d99e232dc231000085899e00a2",  # F10
    "660e1acf58874284bde116a57d853dfb4057e7d8acf69d7026bcdf24e79665a3",  # F11
    "9ba3d1c770bd1d031494bbd49d53e1e0b6b5512a4b3a2d56d274e4bb173a2a00",  # M01
})


def require_f0_literal_bytes(raw: bytes) -> None:
    """Content equality to a pinned synthetic vector; not proof of origin."""
    if type(raw) is not bytes:
        raise SourceNotAdmitted("F0_BYTES_REQUIRED")
    if hashlib.sha256(raw).hexdigest() not in F0_LITERAL_SHA256:
        raise SourceNotAdmitted("UNPINNED_F0_BYTES")


def require_source_scope(*, source: str, admission: str) -> None:
    if source != "F0_SYNTHETIC" or admission != "QA0_F0_SYNTHETIC_ONLY":
        raise SourceNotAdmitted("SOURCE_SCOPE_NOT_APPROVED")


def require_real_corpus(*_args: object, **_kwargs: object) -> None:
    raise SourceNotAdmitted("F1_F2_AND_SCIENTIFIC_TEST_NOT_APPROVED")
