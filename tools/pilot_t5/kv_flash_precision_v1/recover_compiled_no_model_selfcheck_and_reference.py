#!/usr/bin/env python3
"""TTM T5 one-shot recovery of an already-built MSVC candidate.

Repairs DLL lookup for a --self-check ONLY, validates previously generated
F32 reference, preserves original failed STAGE_RECEIPT and original 7/8 FAIL.
NEVER compiles, downloads, trains, loads a model, calls llama_decode,
or runs the 32 fixture*arm science batch.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT_FIXED = Path("D:/WORK/RESEARCH/TokenToModel-Lab")
WORKTREE_REL = "worktrees/ttm-t5-kvflash-preview-20261109"
STAGE_REL = "_tmp/ttm_t5_kvflash_binary_reference_stage_v1_20261110"
RECOVERY_REL = "_tmp/ttm_t5_kvflash_loader_recovery_v1_20261110"
DLL_REL = "_tmp/ttm_t2/build/bin/Release"
REFERENCE_REL = "_tmp/ttm_t5_kvflash_reference_input_v1_20261110/REFERENCE_F32_SYN01_SYN08.jsonl"
SRC_REL = "tools/pilot_t5/kv_flash_precision_v1"
PREREG_REL = "artifacts/qa/ttm-t5-parity/TTM_T5_KV_FLASH_2X2_FRESH_SYNTHETIC_PREREG_20261109.json"
OLD_STAGE_SHA = "235f20131ffd9cfc76738da5956206b2e49ced30b8219864a3d3ce2b4ddb38a7"
OLD_WORKTREE_HEAD = "888adde84e0e4fbe8cbaae801ed4d9687e6b4bb8"
OLD_BINARY_SHA = "0da91785a0882dd1b5a04cce4dc050886b54e0fe0f17e66f66802638b3760537"
REAL_REFERENCE_SHA = "d6f367269df610a4e1c93edbff9a4dcffb7f0e0b6bd5f77247c5c90394de176c"
CPP_BLOB = "bb0e1726e77c92696ffbbb92aa6e6b9aa49ee490"
CMAKE_BLOB = "6f16397d6b6f4ce4a2b299588d5bc6ec83a62861"
PREREG_BLOB = "3b12cc1883ab20e2d9e3a92e6907586c1b4cad36"
CHECKER_BLOB = "2148e674033cf3838e2abb0b1050d3f25700d03b"
VERIFIER_BLOB = "ee16cb05ec438b44c2f83836ef0af7f3edf3280e"
DLL_NAMES = ("llama.dll", "ggml.dll", "ggml-base.dll", "ggml-cpu.dll")


def sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def git_blob(path: Path) -> str:
    b = path.read_bytes()
    return hashlib.sha1(b"blob " + str(len(b)).encode("ascii") + b"\0" + b).hexdigest()


def within(root: Path, path: Path) -> Path:
    p = path.resolve(strict=True)
    if not p.is_relative_to(root):
        raise ValueError("OUTSIDE_TTM_PROJECT")
    if not p.is_file():
        raise ValueError("EXPECTED_FILE_MISSING:" + str(p))
    return p


def run_checked(label: str, argv: list[str], cwd: Path, env: dict, output: Path) -> str:
    """Never shell=True; all logs in new recovery dir, no overwrites."""
    if output.exists():
        raise FileExistsError("LOG_EXISTS:" + label)
    try:
        proc = subprocess.run(
            [str(x) for x in argv],
            cwd=str(cwd), env=env,
            capture_output=True, text=True, errors="replace",
            timeout=45, check=False,
        )
    except subprocess.TimeoutExpired as exc:
        output.write_text("TIMEOUT_AFTER_45_SECONDS\n" + str(exc) + "\n", encoding="utf-8")
        raise RuntimeError(label + "_TIMEOUT") from exc
    output.write_text(
        "ARGV=" + json.dumps([str(x) for x in argv]) + "\n"
        + "EXIT_CODE=" + str(proc.returncode)
        + " EXIT_CODE_HEX=" + hex(proc.returncode & 0xFFFFFFFF) + "\n"
        + "STDOUT:\n" + proc.stdout + "\nSTDERR:\n" + proc.stderr + "\n",
        encoding="utf-8",
    )
    if proc.returncode:
        raise RuntimeError(label + "_EXIT_" + str(proc.returncode)
                           + "_HEX_" + hex(proc.returncode & 0xFFFFFFFF))
    return proc.stdout


def main():
    if os.name != "nt" or sys.version_info[:2] != (3, 12):
        raise RuntimeError("WINDOWS_PYTHON_312_REQUIRED")
    root = ROOT_FIXED.resolve(strict=True)
    if str(root).lower() != str(ROOT_FIXED).lower().replace("/", "\\"):
        # pathlib normalization may retain drive letter case; compare normalized.
        if os.path.normcase(str(root)) != os.path.normcase(str(ROOT_FIXED)):
            raise ValueError("PROJECT_ROOT_CHANGED")
    oldstage = root / STAGE_REL
    work = root / WORKTREE_REL
    newdir = root / RECOVERY_REL
    if newdir.exists():
        raise FileExistsError("RECOVERY_ALREADY_EXISTS_NO_RETRY_NO_OVERWRITE")
    # Require previously emitted evidence and build before creating new receipt.
    oldfile = within(root, oldstage / "STAGE_RECEIPT.json")
    exe = within(root, oldstage / "build/Release/ttm_t5_kvflash_probe.exe")
    source = within(root, work / SRC_REL / "ttm_t5_kvflash_probe_candidate.cpp")
    cmake = within(root, work / SRC_REL / "CMakeLists.txt")
    prereg = within(root, work / PREREG_REL)
    checker = within(root, work / SRC_REL / "check_compiled_constants.py")
    verifier = within(root, work / SRC_REL / "verify_f32_reference_rows.py")
    reference = within(root, root / REFERENCE_REL)
    qa_log = within(root, oldstage / "11_synthetic_python_qa.log")
    failure_log = within(root, oldstage / "14_compiled_no_model_self_check.log")
    dlls = {name: within(root, root / DLL_REL / name) for name in DLL_NAMES}
    if not (work / ".git").exists():
        raise ValueError("OLD_WORKTREE_ABSENT")
    if sha(oldfile) != OLD_STAGE_SHA or sha(exe) != OLD_BINARY_SHA:
        raise ValueError("ORIGINAL_STAGE_OR_COMPILED_BINARY_SHA_MISMATCH")
    if sha(reference) != REAL_REFERENCE_SHA:
        raise ValueError("FROZEN_REFERENCE_SHA_MISMATCH")
    for path, pin in (
        (source, CPP_BLOB), (cmake, CMAKE_BLOB),
        (prereg, PREREG_BLOB), (checker, CHECKER_BLOB), (verifier, VERIFIER_BLOB)
    ):
        if git_blob(path) != pin:
            raise ValueError("FROZEN_GITHUB_SOURCE_BLOB_MISMATCH:" + path.name)
    stage = json.loads(oldfile.read_text("utf-8"))
    if (
        stage.get("status") != "HOLD_STAGE_FAILED_CLOSED"
        or "EXIT_3221225781" not in stage.get("failure", "")
        or stage.get("compiled_executable_sha256") != OLD_BINARY_SHA
        or stage.get("expected_git_head") != OLD_WORKTREE_HEAD
        or stage.get("executed_native_2x2") is not False
        or stage.get("reference") != "NOT_EXECUTED"
    ):
        raise ValueError("ORIGINAL_STAGE_RECEIPT_NOT_FROZEN_FAIL")
    if (
        stage["input_sha256"]["candidate_cpp_sha256"] != sha(source)
        or stage["input_sha256"]["candidate_cmake_sha256"] != sha(cmake)
        or stage["steps"]["11_synthetic_python_qa"]["exit_code"] != 0
        or stage["steps"]["11_synthetic_python_qa"]["log_sha256"] != sha(qa_log)
        or stage["steps"]["13_cmake_build"]["exit_code"] != 0
        or "Ran 13 tests" not in qa_log.read_text("utf-8")
    ):
        raise ValueError("ORIGINAL_BUILD_OR_SYNTHETIC_QA_NOT_ATTESTED")
    if "RETURN_CODE=3221225781" not in failure_log.read_text("utf-8"):
        raise ValueError("ORIGINAL_DLL_LOAD_FAILURE_NOT_ATTESTED")

    # Read-only Git HEAD attestation; does NOT fetch/merge/checkout.
    git = "git.exe"
    probe = subprocess.run([git, "-C", str(work), "rev-parse", "HEAD"],
                           capture_output=True, text=True, timeout=12)
    if probe.returncode or probe.stdout.strip() != OLD_WORKTREE_HEAD:
        raise ValueError("EXISTING_WORKTREE_HEAD_CHANGED")

    newdir.mkdir(parents=True, exist_ok=False)
    result = {
        "schema": "ttm.t5.kvflash.old_binary_loader_recovery_and_ref_qa.v1",
        "status": "HOLD_RECOVERY_STARTED",
        "original_stage_receipt_sha256": OLD_STAGE_SHA,
        "original_stage_status": "HOLD_STAGE_FAILED_CLOSED_PRESERVED",
        "original_failed_selfcheck_log_sha256": sha(failure_log),
        "compiled_existing_binary_sha256": OLD_BINARY_SHA,
        "original_13_tests": "PASS_RECORDED_13_OF_13",
        "original_worktree_head": OLD_WORKTREE_HEAD,
        "dll_directory": str(root / DLL_REL),
        "dll_sha256": {k: sha(v) for k, v in dlls.items()},
        "reference_f32_8x2048_sha256": REAL_REFERENCE_SHA,
        "selfcheck": "NOT_EXECUTED",
        "independent_reference_qa": "NOT_EXECUTED",
        "native_2x2": "0_OF_32_NOT_EXECUTED",
        "historical_strict": "FAIL_7_OF_8_PRESERVED",
        "training": False, "test": False,
        "main": "UNCHANGED", "lineage": "UNCHANGED",
    }

    try:
        # Actual DLL folder lies in _tmp/ttm_t2/build/bin/Release.
        # The failed stage incorrectly used build/upstream_llama/bin/Release.
        env = dict(os.environ)
        env["PATH"] = str(root / DLL_REL) + os.pathsep + env.get("PATH", "")

        print("RECOVERY_STEP=01_existing_compiled_binary_self_check_DLL_PATH", flush=True)
        out = run_checked("01_compiled_self_check", [str(exe), "--self-check"],
                          newdir, env, newdir / "01_compiled_self_check.log")
        parsed = json.loads(out)
        selfcheck_file = newdir / "SELF_CHECK.json"
        with selfcheck_file.open("x", encoding="utf-8") as fp:
            json.dump(parsed, fp, ensure_ascii=False, sort_keys=True)
            fp.write("\n")
        if parsed.get("native_inference") is not False or parsed.get("model_loaded") is not False:
            raise ValueError("SELF_CHECK_UNEXPECTED_MODEL_OR_INFERENCE")
        result["selfcheck"] = "COMPLETED_NO_MODEL"
        result["selfcheck_sha256"] = sha(selfcheck_file)

        print("RECOVERY_STEP=02_compiled_fixture_2x2_constants_vs_prereg", flush=True)
        chk = run_checked("02_compiled_constants",
                [sys.executable, str(checker), "--prereg", str(prereg),
                 "--self-check-json", str(selfcheck_file)],
                newdir, env, newdir / "02_compiled_constants.log")
        check_json = json.loads(chk)
        if check_json.get("status") != "PASS_COMPILED_CONSTANTS_SCOPED":
            raise ValueError("COMPILED_CONSTANTS_NOT_PASS")
        result["compiled_constants"] = "PASS_8_NEW_FIXTURES_X_4_ARMS_NO_DECODE"

        print("RECOVERY_STEP=03_existing_real_p02_reference_independent_schema_qa", flush=True)
        refout = run_checked("03_independent_reference",
                [sys.executable, str(verifier), "--prereg", str(prereg),
                 "--reference", str(reference)],
                newdir, env, newdir / "03_independent_reference.log")
        ref_json = json.loads(refout)
        if (
            ref_json.get("status") != "PASS_REFERENCE_8_OF_8_X_2048_F32_SCHEMA"
            or ref_json.get("reference_sha256") != REAL_REFERENCE_SHA
        ):
            raise ValueError("REFERENCE_INDEPENDENT_QA_NOT_PASS")
        result["independent_reference_qa"] = "PASS_REAL_8X2048_SOURCE_PINNED"
        result["status"] = "PASS_BINARY_SELF_CHECK_AND_REAL_REFERENCE_QA_NATIVE_32_HOLD"
    except Exception as exc:
        result["status"] = "HOLD_RECOVERY_FAILED_CLOSED"
        result["failure"] = type(exc).__name__ + ": " + str(exc)
    finally:
        output = newdir / "RECOVERY_RECEIPT.json"
        with output.open("x", encoding="utf-8") as fp:
            json.dump(result, fp, indent=2, sort_keys=True)
            fp.write("\n")
        print("RECOVERY_STATUS=" + result["status"], flush=True)
        print("RECOVERY_RECEIPT=" + str(output), flush=True)
        print("RECOVERY_RECEIPT_SHA256=" + sha(output), flush=True)
        print("ORIGINAL_STAGE=HOLD_PRESERVED", flush=True)
        print("NATIVE_2X2=0_OF_32_NOT_EXECUTED", flush=True)
        print("STRICT_LOGITS=FAIL_7_OF_8_PRESERVED", flush=True)
    if result["status"] != "PASS_BINARY_SELF_CHECK_AND_REAL_REFERENCE_QA_NATIVE_32_HOLD":
        raise SystemExit(2)


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print("TTM_T5_RECOVERY_DENIED_BEFORE_WRITE:"
              + type(exc).__name__ + ":" + str(exc), file=sys.stderr)
        raise SystemExit(3)
