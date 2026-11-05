"""QA0 F0-only smoke suite. SOURCE-ONLY: not authorized for execution in I0A-S.

No filesystem writes, network, subprocesses, real corpus, or GPT training.
Import/execute only under a *separately approved* QA0 supervisor and
sandbox. This unittest module has no __main__ or auto-run entrypoint.
"""
from __future__ import annotations
import hashlib
import unittest

from src.p01.byte_bpe import (
    BPEContractError, ByteBPE, Merge, encode_merges, learn_merges_f0_qa0_only
)
from src.p01.data_dedup_split import (
    Document, SourceScopeError, classify_f0_documents, assign_splits
)
from qa.p01.f0_fixture_generator import F0_HEX, F0_SHA256
from qa.p01.independent_checker import (
    IndependentCheckError, inspect_m01_design_bytes, validate_receipt_admission
)
from runtime.p01.source_scope_guard import (
    SourceNotAdmitted, require_f0_literal_bytes, require_real_corpus
)
from runtime.p01.windows_job_guard import GuardNotEstablished, start_worker
from runtime.p01.write_quota_broker import BrokerUnavailable, write_file
from runtime.p01.evidence_manifest import EvidenceNotReady, issue_runtime_receipt

QA0_MARKER = "QA0_F0_SYNTHETIC_ONLY"
M01_SHA256 = "11c72190c6f3b757d260c426c357a4de8ff36313495f2299da81638386289e8d"
M01_RULES = (Merge(97, 98, 256), Merge(256, 256, 257))


class QA0F0Smoke(unittest.TestCase):
    def test_b0_full_byte_domain(self):
        raw = bytes(range(256))
        tokenizer = ByteBPE()
        self.assertEqual(tokenizer.encode_bytes(raw), list(range(256)))
        self.assertEqual(tokenizer.decode_bytes(list(range(256))), raw)

    def test_all_f0_literal_hashes_and_roundtrip(self):
        self.assertEqual(set(F0_HEX), {f"F{i:02d}" for i in range(12)})
        b0 = ByteBPE()
        for name in sorted(F0_HEX):
            with self.subTest(name=name):
                raw = bytes.fromhex(F0_HEX[name])
                self.assertEqual(hashlib.sha256(raw).hexdigest(), F0_SHA256[name])
                require_f0_literal_bytes(raw)
                self.assertEqual(b0.decode_bytes(b0.encode_bytes(raw)), raw)

    def test_text_preserves_unicode_bytes_and_rejects_invalid_utf8(self):
        b0 = ByteBPE()
        self.assertNotEqual(b0.encode_text("ắ"), b0.encode_text("a\u0306\u0301"))
        self.assertEqual(b0.decode_text(b0.encode_text("ắ")), "ắ")
        with self.assertRaises(UnicodeEncodeError):
            b0.encode_text("\ud800")
        with self.assertRaises(UnicodeDecodeError):
            b0.decode_text([0xC3, 0x28])

    def test_invalid_token_ids_rejected(self):
        b0 = ByteBPE()
        for bad in [-1, 256, True, 1.5, "65"]:
            with self.subTest(bad=repr(bad)):
                with self.assertRaises(BPEContractError):
                    b0.decode_bytes([bad])

    def test_m01_deterministic_merges_and_independent_golden(self):
        learned = learn_merges_f0_qa0_only(
            [b"abababab"], 258, admission=QA0_MARKER
        )
        self.assertEqual(learned, M01_RULES)
        blob = encode_merges(learned, 258)
        self.assertEqual(len(blob), 47)
        self.assertEqual(hashlib.sha256(blob).hexdigest(), M01_SHA256)
        inspected = inspect_m01_design_bytes(blob)
        self.assertEqual(inspected["merges"], ((97, 98, 256), (256, 256, 257)))
        tokenizer = ByteBPE(learned, 258)
        self.assertEqual(tokenizer.encode_bytes(b"abababab"), [257, 257])
        self.assertEqual(tokenizer.decode_bytes([257, 257]), b"abababab")

    def test_independent_checker_detects_corruption_and_trailing(self):
        blob = bytearray(encode_merges(M01_RULES, 258))
        blob[27] ^= 1
        with self.assertRaises(IndependentCheckError):
            inspect_m01_design_bytes(bytes(blob))
        with self.assertRaises(IndependentCheckError):
            inspect_m01_design_bytes(encode_merges(M01_RULES, 258) + b"\x00")

    def test_bad_documents_rejected_before_attribute_access(self):
        for bad in [
            "not-a-document",
            Document("id", "str-not-bytes", True, True),
            Document(7, b"abababab", True, True),
            Document("id", b"abababab", 1, True),
            Document("id", b"abababab", True, False),
        ]:
            with self.subTest(bad=repr(bad)):
                with self.assertRaises((SourceScopeError, SourceNotAdmitted)):
                    classify_f0_documents([bad], admission=QA0_MARKER)

    def test_canonical_duplicate_group_on_pinned_f02_f03(self):
        docs = [
            Document("F02", bytes.fromhex(F0_HEX["F02"]), True, True),
            Document("F03", bytes.fromhex(F0_HEX["F03"]), True, True),
        ]
        groups = classify_f0_documents(docs, admission=QA0_MARKER)
        self.assertEqual(groups["F02"], groups["F03"])
        with self.assertRaises(SourceScopeError):
            assign_splits(groups, admission=QA0_MARKER)

    def test_unpinned_or_unapproved_inputs_rejected(self):
        with self.assertRaises(SourceNotAdmitted):
            require_f0_literal_bytes(b"unapproved input")
        with self.assertRaises(SourceNotAdmitted):
            learn_merges_f0_qa0_only(
                [b"unapproved input"], 258, admission=QA0_MARKER
            )
        with self.assertRaises(PermissionError):
            learn_merges_f0_qa0_only(
                [b"abababab"], 258, admission="DENIED"
            )
        with self.assertRaises(SourceNotAdmitted):
            classify_f0_documents(
                [Document("x", b"unapproved input", True, True)],
                admission=QA0_MARKER
            )

    def test_runtime_guards_are_fail_closed_not_implemented(self):
        with self.assertRaises(GuardNotEstablished):
            start_worker()
        with self.assertRaises(BrokerUnavailable):
            write_file()
        with self.assertRaises(SourceNotAdmitted):
            require_real_corpus()
        with self.assertRaises(EvidenceNotReady):
            issue_runtime_receipt()
        with self.assertRaises(IndependentCheckError):
            validate_receipt_admission(
                {"operation_id": "DESIGN_ONLY_NO_RUN", "final_status": "PASS"}
            )
