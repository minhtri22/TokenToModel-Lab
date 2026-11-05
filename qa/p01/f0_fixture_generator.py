"""F0 source-only fixture definitions. NO file writes or materialization on import."""
from __future__ import annotations
from dataclasses import dataclass
import hashlib


@dataclass(frozen=True)
class Fixture:
    name: str
    raw_hex: str
    sha256: str


F0_HEX = {
    "F00": "", "F01": "48656c6c6f2c2031323321", "F02": "e1baaf",
    "F03": "61cc86cc81", "F04": "41f09f9880", "F05": "410d0a0942",
    "F06": "007fff", "F07": "c328", "F08": "eda080",
    "F09": "41" * 64, "F10": "41" * 65,
    "F11": "54c3b4692068e1bb8d632041492e20e4bda0e5a5bd",
}
F0_SHA256 = {
    "F00": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
    "F01": "52ce7f8d6d1f955e01b896c8fb38de421b4f9d0a2978fb1e3a3c9f3a6efa80ff",
    "F02": "096b1b5c74b5228a3eefceac7aefcc39432b35b7d24ee4885b1dd06d1045dc77",
    "F03": "0d840a58efa73fdc1557f97b80dabbda05d19cdeeb808319a484f6a66afd05dc",
    "F04": "3c94a0388b52318853918f13698b0677f047c0f298aba9732f8f3f637f652084",
    "F05": "257631603b5242f4a3990499e6134ee263935a1d4433329bff06531313ed2e58",
    "F06": "4234f1064f32788dc9487507f9eeecd0cdf7df6bd010fd1dad8026226e222813",
    "F07": "eddf68639913a3cb8331cdfe7f87559e0beccf2c289c0d90ac4d89b3204004f8",
    "F08": "91a681b998555fb475479817b126c94e57e52011fa1842c5d188795a4a05226b",
    "F09": "d53eda7a637c99cc7fb566d96e9fa109bf15c478410a3f5eb4d4c4e26cd081f6",
    "F10": "836203944f4c0280461ad73d31457c22ba19d1d99e232dc231000085899e00a2",
    "F11": "660e1acf58874284bde116a57d853dfb4057e7d8acf69d7026bcdf24e79665a3",
}


def list_design_fixtures() -> tuple[Fixture, ...]:
    """Return immutable metadata; fixture output files are forbidden in I0A-S."""
    return tuple(Fixture(name, value, F0_SHA256[name]) for name, value in sorted(F0_HEX.items()))


def validate_literal_metadata() -> bool:
    return all(hashlib.sha256(bytes.fromhex(item.raw_hex)).hexdigest() == item.sha256
               for item in list_design_fixtures())
