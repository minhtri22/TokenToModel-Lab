#!/usr/bin/env python3
"""Read-only numerical full-vector audit, never loads a model or declares runner provenance."""
from __future__ import annotations
import argparse
import hashlib
import json
import math
from pathlib import Path

PIN_MAIN = "5d52e32f20021e36f08f284ef9864d3ba36dbead"
PIN_PREREG_GIT_BLOB = "fdcb81064a6c55b3dca5f71e18defff0895c0568"
PIN_GGUF = "5bdc904e6c51af04a4223219f36e6bc2e687f60fd6e17dc24508f3eb7489e4e5"
FIXTURES = {
    "FL01": [97, 98, 99],
    "FL02": [257, 304, 111],
    "FL03": [97, 10, 98],
    "FL04": [88, 267, 628, 195, 160, 111],
}
N = 2048
LIMIT = 0.001

def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def git_blob(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(b"blob " + str(len(data)).encode("ascii") + b"\0" + data).hexdigest()

def in_root(root: Path, target: Path, existing: bool) -> Path:
    p = target.resolve(strict=existing)
    if not p.is_relative_to(root) or p == root:
        raise ValueError("PATH_OUTSIDE_TTM_PROJECT")
    return p

def parse_rows(path: Path, origin: str):
    data = path.read_bytes()
    raw = data.decode("utf-8", errors="strict")
    if not raw.endswith("\n") or raw.count("\n") != 4:
        raise ValueError("FOUR_LINES_WITH_FINAL_NEWLINE_REQUIRED:" + origin)
    rows = {}
    for line in raw.splitlines():
        row = json.loads(line)
        fid = row.get("fixture_id")
        if fid not in FIXTURES or fid in rows:
            raise ValueError("FIXTURE_UNKNOWN_OR_DUPLICATE:" + origin)
        if row.get("token_ids") != FIXTURES[fid]:
            raise ValueError("TOKEN_ID_MISMATCH:" + fid)
        if origin == "ollama":
            if (row.get("schema") != "ttm.ollama.full_logits.runner_pre_sample.v1"
                or row.get("phase") != "PRE_SAMPLING_RAW_F32"
                or row.get("n_vocab") != N):
                raise ValueError("NOT_RAW_RUNNER_PRE_SAMPLE:" + fid)
        elif row.get("source") != "P02_F32_STEP1024_GELU_ERF":
            raise ValueError("NOT_TRUE_P02_REFERENCE:" + fid)
        values = row.get("logits")
        if (not isinstance(values, list) or len(values) != N
            or any(type(x) not in (int, float) or not math.isfinite(x) for x in values)):
            raise ValueError("LOGITS_LENGTH_OR_FINITE_FAILURE:" + fid)
        rows[fid] = values
    if set(rows) != set(FIXTURES):
        raise ValueError("MISSING_EXACT_FIXTURES:" + origin)
    return rows

def compare(ref, other):
    results = []
    for fid in FIXTURES:
        a, b = ref[fid], other[fid]
        diffs = [y-x for x, y in zip(a, b)]
        peak = max(range(N), key=lambda i: abs(diffs[i]))
        top1_r = max(range(N), key=lambda i: a[i])
        top1_o = max(range(N), key=lambda i: b[i])
        err = abs(diffs[peak])
        results.append({
            "fixture_id": fid, "n_logits": N,
            "max_abs": err, "mean_abs": sum(abs(d) for d in diffs)/N,
            "peak_index": peak, "signed_peak_ollama_minus_p02": diffs[peak],
            "top1_reference": top1_r, "top1_ollama": top1_o,
            "top1_equal": top1_r == top1_o,
            "strict_pass": err <= LIMIT and top1_r == top1_o,
        })
    return results

def audit(prereg: Path, reference: Path, ollama: Path):
    if git_blob(prereg) != PIN_PREREG_GIT_BLOB:
        raise ValueError("PREREG_GIT_BLOB_NOT_LOCKED")
    frozen = json.loads(prereg.read_text(encoding="utf-8"))
    if (frozen.get("schema") != "ttm.ollama.full_logits.independent_prereg.v1"
        or frozen.get("base_main_commit") != PIN_MAIN
        or frozen.get("model", {}).get("gguf_f32_sha256") != PIN_GGUF
        or frozen.get("measurement", {}).get("absolute_error_threshold") != LIMIT
        or frozen.get("measurement", {}).get("logits_per_row") != N
        or {x["fixture_id"]: x["token_ids"] for x in frozen["fixtures"]} != FIXTURES):
        raise ValueError("PREREG_CHANGED_OR_INVALID")
    a, b = parse_rows(reference, "reference"), parse_rows(ollama, "ollama")
    records = compare(a, b)
    successes = sum(x["strict_pass"] for x in records)
    return {
        "schema": "ttm.ollama.full_logits.independent_numeric_audit.v1",
        "status": "NUMERIC_PASS_PROVENANCE_PENDING" if successes == 4 else "NUMERIC_FAIL_PROVENANCE_PENDING",
        "full_logits_evaluated": 4*N,
        "threshold": LIMIT, "strict_pass_count": successes,
        "prereg_sha256": digest(prereg), "reference_sha256": digest(reference),
        "ollama_dump_sha256": digest(ollama), "rows": records,
        "runner_provenance_independently_attested": False,
        "end_to_end_ollama_full_logits_pass": False,
        "T5_WINDOWS_F32": "PASS_SCOPED_UNCHANGED",
        "T5_OLLAMA_FULL_LOGITS": "NOT_EXECUTED_UNCHANGED",
    }

def main():
    p = argparse.ArgumentParser()
    for key in ("prereg", "reference", "ollama", "output"):
        p.add_argument("--" + key, type=Path, required=True)
    p.add_argument("--project-root", type=Path, required=True)
    a = p.parse_args()
    root = a.project_root.resolve(strict=True)
    if not root.is_dir():
        raise ValueError("PROJECT_ROOT_NOT_DIRECTORY")
    a.prereg = in_root(root, a.prereg, True)
    a.reference = in_root(root, a.reference, True)
    a.ollama = in_root(root, a.ollama, True)
    a.output = in_root(root, a.output, False)
    if a.output.exists():
        raise FileExistsError("OUTPUT_EXISTS_NO_OVERWRITE")
    result = audit(a.prereg, a.reference, a.ollama)
    with a.output.open("x", encoding="utf-8", newline="\n") as f:
        json.dump(result, f, ensure_ascii=False, indent=2, sort_keys=True)
        f.write("\n")
    print("OLLAMA_FULL_LOGITS_NUMERICAL_STATUS=" + result["status"])
    print("NUMERICAL_AUDIT_SHA256=" + digest(a.output))

if __name__ == "__main__":
    try:
        main()
    except (ValueError, KeyError, TypeError, OSError, json.JSONDecodeError) as exc:
        print("OLLAMA_FULL_LOGITS_TECHNICAL_HOLD=" + str(exc))
        raise SystemExit(2)
