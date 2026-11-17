"""Pure-arithmetic T4 byte-domain eval boundary (no checkpoint, Torch or corpus IO).

The caller provides ALREADY-VALIDATED full-vocabulary gold NLL numbers and
EXACT raw scored UTF-8 bytes + T4 BPE byte spans from a *future* certified
source. This module tests aggregation semantics on synthetic inputs only.
It does NOT validate that NLL came from a model or that token spans are genuine.
Do not promote this source contract to real scientific evaluation.
"""
from __future__ import annotations

import hashlib
import math
from collections.abc import Sequence


class ByteDomainHold(ValueError):
    pass


def arithmetic_bpb(raw_scored_utf8: bytes, t4_rows: Sequence[dict]) -> dict:
    """Aggregate text-target NLL and exclude EOS from BOTH NLL and byte domains.

    T4 EOS is ID 256. T4 merge IDs 257..2047 are regular text tokens,
    NOT BC-v2 role specials; callers may not map them to EOT/PAD/etc.
    A "TEXT" row covers [start,end) of the *scored* raw text, and its NLL
    must be externally derived from full-vocabulary logits (not verified here).
    An "EOS" row has no span or NLL; empty/missing evidence fails closed.
    Byte offsets may bisect a UTF-8 codepoint between adjacent BPE tokens;
    only the COMPLETE joined bytes must decode as valid UTF-8.
    """
    if not isinstance(raw_scored_utf8, bytes) or not raw_scored_utf8:
        raise ByteDomainHold("NO_SCORED_RAW_UTF8")
    try:
        raw_scored_utf8.decode("utf-8", errors="strict")
    except UnicodeDecodeError as exc:
        raise ByteDomainHold("INVALID_UTF8") from exc
    if not isinstance(t4_rows, (tuple, list)) or not t4_rows:
        raise ByteDomainHold("NO_VALID_T4_ROWS")
    end = 0
    nll_sum = 0.0
    count = 0
    eos_seen = False
    for i, row in enumerate(t4_rows):
        if not isinstance(row, dict) or set(row) != {
            "token_id", "kind", "start", "end", "gold_nll_nats"
        }:
            raise ByteDomainHold("ROW_SCHEMA_MISMATCH:" + str(i))
        token_id, kind = row["token_id"], row["kind"]
        if type(token_id) is not int or not (0 <= token_id < 2048):
            raise ByteDomainHold("T4_TOKEN_RANGE:" + str(i))
        if kind == "EOS":
            if token_id != 256 or row["start"] is not None or row["end"] is not None or row["gold_nll_nats"] is not None:
                raise ByteDomainHold("EOS_MUST_HAVE_NO_RAW_BYTES_OR_NLL")
            eos_seen = True
            continue
        if kind != "TEXT" or token_id == 256 or eos_seen:
            raise ByteDomainHold("T4_TEXT_ROLE_OR_EOS_ALIAS")
        a, b, value = row["start"], row["end"], row["gold_nll_nats"]
        if type(a) is not int or type(b) is not int or a != end or b <= a or b > len(raw_scored_utf8):
            raise ByteDomainHold("BYTE_SPAN_COVERAGE_OR_OVERLAP")
        if type(value) not in (int, float) or not math.isfinite(value) or value < 0:
            raise ByteDomainHold("NONFINITE_OR_NEGATIVE_NLL")
        nll_sum += float(value)
        end = b
        count += 1
    if end != len(raw_scored_utf8) or count == 0:
        raise ByteDomainHold("RAW_TEXT_NOT_COVERED")
    if not math.isfinite(nll_sum):
        raise ByteDomainHold("NLL_OVERFLOW")
    return {
        "schema": "ttm.pm.real_gpt.byte_domain_arithmetic.v1",
        "status": "PASS_SYNTHETIC_ARITHMETIC_ONLY",
        "source_sha256_of_supplied_bytes": hashlib.sha256(raw_scored_utf8).hexdigest(),
        "text_target_count": count,
        "valid_utf8_bytes": len(raw_scored_utf8),
        "text_nll_sum_nats": nll_sum,
        "text_val_bpb_arithmetic_only": nll_sum / (math.log(2.0) * len(raw_scored_utf8)),
        "stop_loss_included": False,
        "full_vocab_nll_provenance": "UNVERIFIED_EXTERNAL_A_SCORER_REQUIRED",
        "raw_byte_span_authenticity": "UNVERIFIED_REAL_SOURCE_REQUIRED",
        "authorized_for_real_science": False,
    }
