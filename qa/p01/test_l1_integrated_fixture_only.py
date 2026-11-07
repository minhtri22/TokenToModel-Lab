"""TTM P01 L1: additive algorithm integration QA, synthetic-only, no science.

Runs with standard unittest. This module has no import-time side effects, IO,
network, shell, corpus reads, source changes, training, or TEST access.
Only the in-process classifier *fixture hash admission function* is patched
inside a context manager; runtime.source_scope_guard remains unchanged.
Do not interpret fixture PASS as real-corpus admission or Windows S1 PASS.
"""
from __future__ import annotations

from collections import Counter
import hashlib
import unittest
from unittest.mock import patch

from src.p01 import data_dedup_split as ds
from src.p01.byte_bpe import Merge, learn_merges_f0_qa0_only
from runtime.p01.source_scope_guard import SourceNotAdmitted, require_f0_literal_bytes
from qa.p01.f0_fixture_generator import F0_HEX

ADMISSION = "QA0_F0_SYNTHETIC_ONLY"
PREFIX = b"TTM-P01-GROUP-V1\x00"


def _corpus():
    """34 artificial records, 30 expected components; no real text source."""
    raw_a = b"abcdefghijklmnopqrstuvwxyz"
    raw_b = b"ab0defg1ijklmnopqrstuvwxyz"
    raw_c = b"ab0defg1ijkl2nopq3stuvwxyz"
    records = [
        ds.Document("bridge_A", raw_a, True, True),
        ds.Document("bridge_B", raw_b, True, True),
        ds.Document("bridge_C", raw_c, True, True),
    ]
    for i in range(29):
        raw = hashlib.sha256(f"TTM-P01-QA-ONLY-{i:02d}".encode("ascii")).hexdigest().encode("ascii")
        records.append(ds.Document(f"single_{i:02d}", raw, True, True))
        if i == 0:
            records.append(ds.Document("single_00_raw_copy", raw, True, True))
            records.append(ds.Document("single_00_canonical_copy", raw.upper() + b"\r\n", True, True))
    assert len(records) == 34
    return records


def _fixture_guard(records):
    permitted = {hashlib.sha256(item.raw).digest() for item in records}

    def admit(raw):
        if type(raw) is not bytes or hashlib.sha256(raw).digest() not in permitted:
            raise SourceNotAdmitted("QA_FIXTURE_HASH_NOT_ALLOWED")
    return admit


def _cross_split_overlap(records, labels, group_ids):
    per_label = {split: {"group": set(), "raw": set(), "canonical": set()}
                 for split in ("TRAIN", "VALIDATION", "TEST")}
    for record in records:
        entry = per_label[labels[record.document_id]]
        entry["group"].add(group_ids[record.document_id])
        entry["raw"].add(hashlib.sha256(record.raw).hexdigest())
        canonical = ds.canonical_key(record.raw).encode("utf-8")
        entry["canonical"].add(hashlib.sha256(canonical).hexdigest())
    counts = {}
    for dimension in ("group", "raw", "canonical"):
        counts[dimension] = sum(
            len(per_label[a][dimension] & per_label[b][dimension])
            for a, b in (("TRAIN", "VALIDATION"), ("TRAIN", "TEST"), ("VALIDATION", "TEST"))
        )
    return counts


class P01L1SyntheticOnlyIntegratedQA(unittest.TestCase):
    def test_01_bpe_tie_breaker_on_pinned_f0_only(self):
        f01 = bytes.fromhex(F0_HEX["F01"])
        result = learn_merges_f0_qa0_only([f01, f01], 257, admission=ADMISSION)
        self.assertEqual(result, (Merge(32, 49, 256),))

    def test_02_bpe_never_counts_cross_document_pair(self):
        # F07 ends in byte 40, F02 starts in byte 225; fake join pair
        # (40,225) repeats twice and wins a lexicographic tie IF concatenated.
        f07 = bytes.fromhex(F0_HEX["F07"])
        f02 = bytes.fromhex(F0_HEX["F02"])
        result = learn_merges_f0_qa0_only([f07, f02, f07, f02], 257, admission=ADMISSION)
        self.assertEqual(result, (Merge(186, 175, 256),))

    def test_03_bridge_oracle_is_transitive_not_all_pairwise(self):
        a, b, c = [record.raw.decode("ascii") for record in _corpus()[:3]]
        self.assertTrue(ds.near_duplicate(a, b))
        self.assertTrue(ds.near_duplicate(b, c))
        self.assertFalse(ds.near_duplicate(a, c))

    def test_04_34_document_full_classify_split_fixture_algorithm(self):
        records = _corpus()
        with patch.object(ds, "require_f0_literal_bytes", side_effect=_fixture_guard(records)):
            groups = ds.classify_f0_documents(records, admission=ADMISSION)
        self.assertEqual(len(groups), 34)
        self.assertEqual(len(set(groups.values())), 30)
        self.assertEqual(len(set(groups[name] for name in ("bridge_A", "bridge_B", "bridge_C"))), 1)
        self.assertEqual(len(set(groups[name] for name in
                                 ("single_00", "single_00_raw_copy", "single_00_canonical_copy"))), 1)
        expected_bridge_id = hashlib.sha256(
            PREFIX + min(hashlib.sha256(r.raw).digest() for r in records[:3])
        ).hexdigest()
        self.assertEqual(groups["bridge_A"], expected_bridge_id)
        labels = ds.assign_splits(groups, admission=ADMISSION, seed=20261105)
        count = Counter({label: sum(1 for gid in set(groups.values())
                                    if any(labels[doc] == label and group == gid
                                           for doc, group in groups.items()))
                         for label in ("TRAIN", "VALIDATION", "TEST")})
        self.assertEqual(dict(count), {"TRAIN": 24, "VALIDATION": 3, "TEST": 3})
        self.assertEqual(_cross_split_overlap(records, labels, groups),
                         {"group": 0, "raw": 0, "canonical": 0})

    def test_05_order_independence_under_in_process_fixture_only(self):
        records = _corpus()
        with patch.object(ds, "require_f0_literal_bytes", side_effect=_fixture_guard(records)):
            forward = ds.classify_f0_documents(records, admission=ADMISSION)
            reverse = ds.classify_f0_documents(list(reversed(records)), admission=ADMISSION)
        self.assertEqual(forward, reverse)
        self.assertEqual(ds.assign_splits(forward, admission=ADMISSION),
                         ds.assign_splits(reverse, admission=ADMISSION))

    def test_06_independent_overlap_audit_detects_introduced_leak(self):
        records = _corpus()
        with patch.object(ds, "require_f0_literal_bytes", side_effect=_fixture_guard(records)):
            groups = ds.classify_f0_documents(records, admission=ADMISSION)
        labels = ds.assign_splits(groups, admission=ADMISSION)
        self.assertEqual(sum(_cross_split_overlap(records, labels, groups).values()), 0)
        corrupted = dict(labels)
        current = labels["single_00_raw_copy"]
        corrupted["single_00_raw_copy"] = next(x for x in ("TRAIN", "VALIDATION", "TEST") if x != current)
        overlaps = _cross_split_overlap(records, corrupted, groups)
        self.assertGreaterEqual(overlaps["group"], 1)
        self.assertGreaterEqual(overlaps["raw"], 1)
        self.assertGreaterEqual(overlaps["canonical"], 1)

    def test_07_unpatched_f1_block_and_under_30_groups(self):
        records = _corpus()
        with self.assertRaises(SourceNotAdmitted):
            require_f0_literal_bytes(records[0].raw)
        with self.assertRaises(SourceNotAdmitted):
            ds.classify_f0_documents(records, admission=ADMISSION)
        insufficient = {f"doc{i}": hashlib.sha256(f"gid{i}".encode()).hexdigest()
                        for i in range(29)}
        with self.assertRaisesRegex(ds.SourceScopeError, "INSUFFICIENT_GROUPS"):
            ds.assign_splits(insufficient, admission=ADMISSION)
        unreviewed = [ds.Document("bad", records[0].raw, True, False)]
        with patch.object(ds, "require_f0_literal_bytes", side_effect=_fixture_guard(records)):
            with self.assertRaisesRegex(ds.SourceScopeError, "QUARANTINE_OR_REJECT"):
                ds.classify_f0_documents(unreviewed, admission=ADMISSION)


# Deliberately no automatic test runner: invoke explicitly with
# python -m unittest qa.p01.test_l1_integrated_fixture_only -v.
