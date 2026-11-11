#!/usr/bin/env python3
"""Standard-library static/contract checks only; no training or inference."""
from __future__ import annotations
import hashlib
import importlib.util
import json
import sys
from pathlib import Path

SRC = Path(__file__).with_name("external_knowledge_fixture.py")
spec = importlib.util.spec_from_file_location("vm_external_fixture", SRC)
module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = module
spec.loader.exec_module(module)
checks = {}


def check(name, condition):
    checks[name] = bool(condition)
    if not condition:
        raise AssertionError(name)


def run() -> dict:
    train = module.build("train")
    dev = module.build("dev")
    check("train_count", len(train) == 256)
    check("dev_count", len(dev) == 64)
    check("split_ids_disjoint", set(x["case_id"] for x in train).isdisjoint(x["case_id"] for x in dev))
    check("target_keys_disjoint", set(x["target_key"] for x in train).isdisjoint(x["target_key"] for x in dev))
    check("answer_not_in_question", all(x["answer"] not in x["question"] for x in train + dev))
    check("answer_balanced_train", all(sum(x["answer"] == l for x in train) == 16 for l in module.LABELS))
    check("answer_balanced_dev", all(sum(x["answer"] == l for x in dev) == 4 for l in module.LABELS))
    check("exactly_one_right_fact", all(sum(f["key"] == x["target_key"] and f["value"] == x["answer"] for f in x["correct_memory"]) == 1 for x in train + dev))
    check("wrong_excludes_gold", all(all(f["value"] != x["answer"] for f in x["wrong_memory"]) for x in train + dev))
    check("same_key_order_and_card_count", all([f["key"] for f in x["correct_memory"]] == [f["key"] for f in x["wrong_memory"]] and len(x["correct_memory"]) == 3 for x in train + dev))
    check("single_changed_value", all(sum(a["value"] != b["value"] for a, b in zip(x["correct_memory"], x["wrong_memory"])) == 1 for x in train + dev))
    check("no_memory_is_empty_and_masked", all(x["none_memory"] == [] and x["no_memory_mask_all"] for x in train + dev))
    check("record_order_varies", len(set(x["target_record_rank"] for x in train)) == 3)
    check("question_templates_varied", len(set(x["question"].split("archive object")[0] for x in train)) >= 2)
    check("deterministic_train", module.stable_json(train) == module.stable_json(module.build("train")))
    check("deterministic_dev", module.stable_json(dev) == module.stable_json(module.build("dev")))
    # DO NOT materialize an actual TEST dataset. Only assert hard fail without secret.
    try:
        module.build("test")
    except ValueError as e:
        check("test_requires_private_secret", "TEST_SECRET_REQUIRED" in str(e))
    else:
        check("test_requires_private_secret", False)
    # Mock-only TEST checks prove code boundaries but are NOT a seal or a source of TEST.
    qa_secret = "NON_SCIENCE_QA_ONLY_DO_NOT_USE_AS_TEST_SEED"
    mock = module.build("test", secret=qa_secret)
    check("mock_test_count", len(mock) == 64)
    check("mock_test_disjoint", set(x["target_key"] for x in mock).isdisjoint(x["target_key"] for x in train + dev))
    check("mock_test_balanced", all(sum(x["answer"] == l for x in mock) == 4 for l in module.LABELS))
    check("mock_test_requires_different_secret", module.make_case("test",0,qa_secret)["target_key"] != module.make_case("test",0,"ANOTHER_QA_NONSCIENCE_DO_NOT_USE_AS_TEST_SECRET" )["target_key"])
    check("schema_pinned", module.SCHEMA == "ttm.vector_memory.external_knowledge.fixture.v1")
    result = {
        "schema": "ttm.vector_memory.external_knowledge.static_qa.v1",
        "run_type": "DESIGN_ONLY_NO_MODEL_INFERENCE_NO_TRAINING_NO_TEST_MATERIALIZATION",
        "status": "PASS" if all(checks.values()) else "FAIL",
        "checks": checks,
        "checks_passed": sum(checks.values()),
        "checks_total": len(checks),
        "train_cases": len(train),
        "dev_cases": len(dev),
        "real_test_cases_materialized": 0,
        "test_secret_status": "NOT_ISSUED_NOT_SEALED",
        "train_sha256": hashlib.sha256(module.stable_json(train)).hexdigest(),
        "dev_sha256": hashlib.sha256(module.stable_json(dev)).hexdigest(),
        "runner_sha256": hashlib.sha256(SRC.read_bytes()).hexdigest(),
        "limitations": ["No tokenizer/checkpoint integration or hidden-state retrieval measured",
                        "No real TEST secret issued or held-out TEST dataset sealed",
                        "Synthetic arbitrary object-tag facts are not real-world semantic knowledge",
                        "TRAIN/DEV fixtures are generated to validate contract only, not model performance"],
    }
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return result


if __name__ == "__main__":
    run()
