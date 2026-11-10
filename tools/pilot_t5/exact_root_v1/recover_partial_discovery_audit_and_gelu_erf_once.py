#!/usr/bin/env python3
"""TTM T5 V2 finite continuation of partial one-shot.

Old discovery remains immutable. Re-audit saved trace_only native D01/D02;
then compile and execute ONLY the previously unexecuted GELU_ERF variant
once, on exactly the same authorized two discovery fixtures.

No original llama vendor mutation, no old eight or 32 native rerun, no
confirmatory C01..C04, no model training or main/lineage writes. Results
must be adjudicated separately; this is not proof of root cause.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path("D:/WORK/RESEARCH/TokenToModel-Lab")
ORIGINAL = "_tmp/ttm_t5_exact_root_discovery_run_v1_20261110"
ISOLATION = "_tmp/ttm_t5_exact_root_v1_20261110"
RECOVERY = "_tmp/ttm_t5_exact_root_discovery_recovery_v2_20261110"
WORK = "worktrees/ttm-t5-kvflash-preview-20261109"
GGUF = "_tmp/ttm_t5_trained_f32_v1/TTM-Small4M-T4-step1024-F32.gguf"
GGUF_SHA = "5bdc904e6c51af04a4223219f36e6bc2e687f60fd6e17dc24508f3eb7489e4e5"
OLD_RECEIPT_SHA = "e2cbc797e133a7e4fc4d949293dd9bd847b881e18b39f3c72bcfa9debfbc8e96"
OLD_ISOLATION_SHA = "e6462e8cc7731ce99a057b045ced88154cd1d6b8bda6a925c6fe19155e0b3522"
REF_SHA = "9cc5fc2db1f95e7e863a285eb279b28b7a383b81a4f890d7ec0f79b788b995e0"
REF_FILE = "TTM_T5_D01D02_P02_TRUE_SIGNED_TRACE_20261110.jsonl"
PREREG_BLOB = "82fdd9fe716579181db648caa69170fb63d115a6"
ORIGINAL_WORK_HEAD = "4cd50e991c383809c804691b50be29624f39eebf"
ORIGINAL_CPP_BLOB = "80c18b6eb9272ee9457f4ffee761e1f0d0625c6b"
ORIGINAL_CMAKE_BLOB = "e19520ac4cc73a68fa036b9842260e569fe0cdc8"
V1_AUDIT_BLOB = "cf6a39f5e763b428fefd0d4c1bd5d0683cd78997"
V2_AUDIT_BLOB = "REPLACE_V2_BLOB"
V2_TEST_BLOB = "REPLACE_V2_TEST_BLOB"
LLAMA_COMMIT = "372dc5ca157276beb6c67b2e92477e8d662e964a"
B_GRAPH_SHA = "df553f77f4d481877455dde37a96b19e77e4aefd674879e14bcf55b9e2a2dd2c"
B_GPT2_SHA = "59d1685da8f44ed420af8852c987a6c72e0d028c8304931f05a9e90a5c03f06e"
ARM = [{"id": "S1_F32_NO_FLASH", "kv": "F32", "flash": "DISABLED"}]
FIX = [("D01", [1281]), ("D02", [1406, 971, 566, 1092, 1587])]
DLLS = ("llama.dll", "ggml.dll", "ggml-base.dll", "ggml-cpu.dll")
OWNER_SCOPE = "I_APPROVE_RESUME_ONLY_TTM_T5_UNRUN_GELU_ERF_D01_D02"

def sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()

def blob(path: Path) -> str:
    b = path.read_bytes()
    return hashlib.sha1(b"blob " + str(len(b)).encode() + b"\0" + b).hexdigest()

def member(root: Path, path: Path, regular: bool = True) -> Path:
    p = path.resolve(strict=True)
    if not p.is_relative_to(root) or (regular and not p.is_file()):
        raise ValueError("PROJECT_BOUNDED_EXISTING_FILE_REQUIRED:" + str(path))
    return p

def run(label, argv, cwd, logfile, timeout=180, extra_env=None):
    if logfile.exists():
        raise FileExistsError("RECOVERY_LOG_ALREADY_EXISTS:" + label)
    env = dict(os.environ)
    env["TEMP"] = str(cwd)
    env["TMP"] = str(cwd)
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    if extra_env:
        env.update(extra_env)
    try:
        p = subprocess.run([str(x) for x in argv], cwd=str(cwd),
                           env=env, capture_output=True, text=True,
                           errors="replace", check=False, timeout=timeout)
        logfile.write_text(
            "ARGV=" + json.dumps([str(x) for x in argv]) +
            "\nRETURN_CODE=" + str(p.returncode) +
            "\nSTDOUT:\n" + p.stdout + "\nSTDERR:\n" + p.stderr +
            "\n", encoding="utf-8")
        if p.returncode:
            raise RuntimeError(label + "_EXIT_" + str(p.returncode) + "_SEE_LOG")
        print("RECOVERY_STEP=" + label, flush=True)
        return p.stdout
    except subprocess.TimeoutExpired as e:
        logfile.write_text("TIMEOUT_NO_RETRY:" + str(e) + "\n", encoding="utf-8")
        raise RuntimeError(label + "_TIMEOUT_NO_RETRY") from e

def audit_cmd(python, auditor, prereg, ref, trace, logits, output):
    return [python, auditor, "--prereg", prereg, "--reference", ref,
            "--native-trace", trace, "--native-logits", logits,
            "--output", output]

def check_report(report: Path):
    x = json.loads(report.read_text("utf-8"))
    if (x["schema"] != "ttm.t5.firstop.scoped_independent_signed_tensor_comparison.v2"
        or x["status"] != "PASS_TRACE_PROTOCOL_MEASURED_CAUSE_NOT_PROVEN"
        or x["repair_scope"] != "V2_SINGLETON_BATCH_FINAL_NORM_AND_OUTPUT_ONLY"
        or set(x["rows"]) != {"D01", "D02"}
        or x["strict_threshold"] != 0.001
        or x["actual_native_decodes"] != 2
        or x["confirmatory_not_accessed"] is not True):
        raise ValueError("V2_REPORT_SCHEMA_OR_SCOPE_MISMATCH")
    for k in ("D01", "D02"):
        if len(x["rows"][k]["stages"]) < 10:
            raise ValueError("MISSING_TENSOR_COVERAGE:" + k)
    return x

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--project-root", required=True, type=Path)
    ap.add_argument("--auditor-v2", required=True, type=Path)
    ap.add_argument("--test-v2", required=True, type=Path)
    ap.add_argument("--approve-recovery-scope", required=True)
    args = ap.parse_args()
    if (os.name != "nt" or sys.version_info[:2] != (3, 12)
        or args.approve_recovery_scope != OWNER_SCOPE):
        raise ValueError("WINDOWS_PY312_AND_EXACT_OWNER_SCOPE_REQUIRED")
    root = args.project_root.resolve(strict=True)
    if os.path.normcase(str(root)) != os.path.normcase(str(ROOT)):
        raise ValueError("EXACT_PROJECT_ROOT_REQUIRED")
    old = member(root, root / ORIGINAL, regular=False)
    isolation = member(root, root / ISOLATION, regular=False)
    work = member(root, root / WORK, regular=False)
    auditor = member(root, args.auditor_v2)
    test = member(root, args.test_v2)
    if blob(auditor) != V2_AUDIT_BLOB or blob(test) != V2_TEST_BLOB:
        raise ValueError("RECOVERY_AUDITOR_OR_UNIT_TEST_SOURCE_BLOB_CHANGED")
    source = member(root, work / "tools/pilot_t5/exact_root_v1", regular=False)
    cpp = member(root, source / "ttm_t5_firstop_trace_probe.cpp")
    cmake = member(root, source / "CMakeLists.txt")
    old_auditor = member(root, source / "independent_firstop_signed_tensor_audit.py")
    prereg = member(root, work /
        "artifacts/qa/ttm-t5-parity/TTM_T5_EXACT_FIRST_OP_NEW_FIXTURES_INTEGRATED_PREREG_20261110.json")
    if (blob(cpp) != ORIGINAL_CPP_BLOB or blob(cmake) != ORIGINAL_CMAKE_BLOB
        or blob(old_auditor) != V1_AUDIT_BLOB or blob(prereg) != PREREG_BLOB):
        raise ValueError("ORIGINAL_SOURCE_OR_PREREG_CHANGED")
    head = subprocess.run(["git.exe", "-C", str(work), "rev-parse", "HEAD"],
                          capture_output=True, text=True, timeout=20)
    if head.returncode or head.stdout.strip() != ORIGINAL_WORK_HEAD:
        raise ValueError("OLD_WORKTREE_HEAD_CHANGED_OR_DIRTY")
    status = subprocess.run(["git.exe", "-C", str(work), "status", "--porcelain"],
                            capture_output=True, text=True, timeout=20)
    if status.returncode or status.stdout.strip():
        raise ValueError("WORKTREE_NOT_CLEAN")
    gguf = member(root, root / GGUF)
    if sha(gguf) != GGUF_SHA:
        raise ValueError("ORIGINAL_F32_GGUF_CHANGED")
    old_receipt = member(root, old / "DISCOVERY_RUN_RECEIPT.json")
    isolated_receipt = member(root, isolation / "SOURCE_ISOLATION_RECEIPT.json")
    if (sha(old_receipt) != OLD_RECEIPT_SHA or
        sha(isolated_receipt) != OLD_ISOLATION_SHA):
        raise ValueError("IMMUTABLE_ORIGINAL_STAGE_RECEIPT_SHA_CHANGED")
    old_meta = json.loads(old_receipt.read_text("utf-8"))
    isolation_meta = json.loads(isolated_receipt.read_text("utf-8"))
    if (old_meta["status"] != "HOLD_DISCOVERY_FAILED_OR_PARTIAL_NO_RERUN"
        or old_meta["failure"] !=
            "RuntimeError:trace_only_12_independent_signed_audit_FAILED_EXIT_2_READ_LOG"
        or old_meta["confirmatory"] != "NOT_EXECUTED"
        or old_meta["variants"] != {}
        or isolation_meta["status"] != "PASS_TWO_ISOLATED_SOURCE_VARIANTS_READY_FOR_BUILD"
        or isolation_meta["pinned_llama_commit"] != LLAMA_COMMIT):
        raise ValueError("ORIGINAL_STAGE_STATE_NOT_EXPECTED")
    ref = member(root, old / REF_FILE)
    if sha(ref) != REF_SHA:
        raise ValueError("P02_REFERENCE_CHANGED")
    a = old / "trace_only"
    old_log = member(root, a / "12_independent_audit.log").read_text("utf-8")
    native_log = member(root, a / "11_native.log").read_text("utf-8")
    self_log = member(root, a / "10_self_check.log").read_text("utf-8")
    if ("FIRSTOP_AUDIT_FAIL_CLOSED:FINAL_STAGE_SHAPE_NOT_ALIGNED:result_norm"
        not in old_log or "\nEXIT_CODE=2\n" not in old_log
        or "T5_FIRST_OP_DISCOVERY_COMPLETE_ROWS_2" not in native_log
        or "\nEXIT_CODE=0\n" not in native_log
        or '"native_inference":false' not in self_log):
        raise ValueError("ORIGINAL_NATIVE_SUCCESS_AND_AUDIT_BUG_NOT_ATTESTED")
    trace_a = member(root, a / "D01_D02_F32_OFF_NATIVE.jsonl.trace.jsonl")
    logits_a = member(root, a / "D01_D02_F32_OFF_NATIVE.jsonl")
    b_source = member(root, isolation / "trace_gelu_erf", regular=False)
    b_files = isolation_meta["trace_gelu_erf"]
    graph = member(root, b_source / "src/llama-graph.cpp")
    gpt2 = member(root, b_source / "src/models/gpt2.cpp")
    if (sha(graph) != B_GRAPH_SHA or sha(gpt2) != B_GPT2_SHA
        or b_files["gpt2_activation"] != "GELU_ERF"
        or b_files["graph_sha256"] != B_GRAPH_SHA
        or b_files["gpt2_sha256"] != B_GPT2_SHA):
        raise ValueError("PREEXISTING_GELU_ERF_VARIANT_SOURCE_CHANGED")
    target = root / RECOVERY
    if target.exists():
        raise FileExistsError("RECOVERY_ALREADY_EXISTS_ONE_SHOT_NO_REPEAT")
    target.mkdir(parents=True, exist_ok=False)
    report = {"schema": "ttm.t5.firstop.partial_recovery_v2.v1",
              "status": "HOLD_RECOVERY_STARTED",
              "old_one_shot_receipt_sha256": OLD_RECEIPT_SHA,
              "old_audit_failure": old_meta["failure"],
              "old_trace_only_native_reexecuted": False,
              "new_native_gelu_erf_executions": 0,
              "historical_8_32_replayed": False,
              "confirmatory_C01_C04": "NOT_EXECUTED",
              "training": False, "TEST": False, "main": "UNCHANGED",
              "lineage": "UNCHANGED", "science": "UNADJUDICATED",
              "inputs_sha256": {"original_GGUF": GGUF_SHA,
                                "P02_reference": REF_SHA,
                                "original_native_trace": sha(trace_a),
                                "original_native_logits": sha(logits_a),
                                "source_isolation_receipt": OLD_ISOLATION_SHA},
              "audit_v2_blob": V2_AUDIT_BLOB,
              "test_v2_blob": V2_TEST_BLOB,
              "variants": {}}
    try:
        run("01_v2_shape_unit_tests", [sys.executable, "-B", test],
            target, target / "01_v2_shape_unit_tests.log", 45)
        output_a = target / "A_EXISTING_TRACE_ONLY_SIGNED_AUDIT_V2.json"
        run("02_audit_saved_trace_only_no_native_call",
            audit_cmd(sys.executable, auditor, prereg, ref,
                      trace_a, logits_a, output_a),
            target, target / "02_reaudit_saved_A.log", 120)
        a_summary = check_report(output_a)
        report["variants"]["trace_only"] = {
            "native_reexecuted": False, "audit_sha256": sha(output_a),
            "first_over_1e_minus_5": {k: v["first_over_1e_minus_5"]
                                     for k, v in a_summary["rows"].items()},
            "strict_max_abs": {k: v["strict_max_abs"]
                                for k, v in a_summary["rows"].items()}}
        # B is the only newly executed native process.
        b = target / "trace_gelu_erf"
        b.mkdir(parents=True, exist_ok=False)
        build = b / "llama_build"
        probe_build = b / "probe_build"
        flags = ["-G", "Visual Studio 17 2022", "-A", "x64",
                 "-DBUILD_SHARED_LIBS=ON", "-DLLAMA_BUILD_TESTS=OFF",
                 "-DLLAMA_BUILD_EXAMPLES=OFF", "-DLLAMA_CURL=OFF",
                 "-DGGML_NATIVE=ON"]
        run("03_B_configure_llama",
            ["cmake.exe", "-S", b_source, "-B", build, *flags],
            b, b / "03_config_llama.log", 180)
        run("04_B_build_llama",
            ["cmake.exe", "--build", build, "--config", "Release",
             "--target", "llama", "--parallel", "4"],
            b, b / "04_build_llama.log", 900)
        run("05_B_configure_probe",
            ["cmake.exe", "-S", source, "-B", probe_build,
             "-G", "Visual Studio 17 2022", "-A", "x64",
             "-DLLAMA_SOURCE_ROOT=" + str(b_source),
             "-DLLAMA_BUILD_ROOT=" + str(build)],
            b, b / "05_config_probe.log", 180)
        run("06_B_build_probe",
            ["cmake.exe", "--build", probe_build, "--config",
             "Release", "--target", "ttm_t5_firstop_trace_probe",
             "--parallel", "4"],
            b, b / "06_build_probe.log", 600)
        executable = member(root, probe_build /
                            "Release/ttm_t5_firstop_trace_probe.exe")
        dll_dir = member(root, build / "bin/Release", regular=False)
        dlls = {name: member(root, dll_dir / name) for name in DLLS}
        env = {"PATH": str(dll_dir) + os.pathsep + os.environ.get("PATH", "")}
        check = run("07_B_no_model_self_check", [executable, "--self-check"],
                    b, b / "07_self_check.log", 45, env)
        values = json.loads(check)
        if (values.get("schema") !=
            "ttm.t5.firstop.discover_two.compiled_constants.v1"
            or values.get("model_loaded") is not False
            or values.get("native_inference") is not False
            or values.get("arms") != ARM
            or [(z["fixture_id"], z["token_ids"])
                for z in values.get("fixtures", [])] != FIX):
            raise ValueError("B_BINARY_SELF_CHECK_MISMATCH")
        out_native = b / "B_NEW_D01_D02_NATIVE.jsonl"
        print("NEW_B_GELU_ERF_NATIVE_D01_D02=STARTED_ONCE", flush=True)
        native_stdout = run("08_B_native_once",
            [executable, root, gguf, out_native],
            b, b / "08_B_native.log", 300, env)
        if "T5_FIRST_OP_DISCOVERY_COMPLETE_ROWS_2" not in native_stdout:
            raise ValueError("B_TWO_NATIVE_COMPLETION_MARKER_MISSING")
        report["new_native_gelu_erf_executions"] = 2
        trace_b = member(root, Path(str(out_native) + ".trace.jsonl"))
        native_b = member(root, out_native)
        report_b = b / "B_NEW_GELU_ERF_SIGNED_AUDIT_V2.json"
        run("09_B_independent_signed_audit",
            audit_cmd(sys.executable, auditor, prereg,
                      ref, trace_b, native_b, report_b),
            b, b / "09_B_independent_audit.log", 120)
        b_summary = check_report(report_b)
        report["variants"]["trace_gelu_erf"] = {
            "native_reexecuted": False,
            "executable_sha256": sha(executable),
            "DLL_SHA256": {n: sha(f) for n, f in dlls.items()},
            "native_sha256": sha(native_b),
            "trace_sha256": sha(trace_b),
            "audit_sha256": sha(report_b),
            "first_over_1e_minus_5": {k: v["first_over_1e_minus_5"]
                                     for k, v in b_summary["rows"].items()},
            "strict_max_abs": {k: v["strict_max_abs"]
                                for k, v in b_summary["rows"].items()}}
        report["status"] = "RECOVERY_TWO_VARIANTS_AUDITED_DISCOVERY_UNADJUDICATED"
    except Exception as exc:
        report["status"] = "HOLD_RECOVERY_FAILED_OR_PARTIAL_DO_NOT_RERUN"
        report["failure"] = type(exc).__name__ + ":" + str(exc)
    finally:
        receipt = target / "RECOVERY_V2_RECEIPT.json"
        with receipt.open("x", encoding="utf-8", newline="\n") as f:
            json.dump(report, f, sort_keys=True, indent=2, ensure_ascii=False)
            f.write("\n")
        print("RECOVERY_V2_STATUS=" + report["status"], flush=True)
        print("RECOVERY_V2_RECEIPT=" + str(receipt), flush=True)
        print("RECOVERY_V2_RECEIPT_SHA256=" + sha(receipt), flush=True)
        print("OLD_DISCOVERY=IMMUTABLE; OLD_NATIVE_A_REPLAY=NO; "
              "CONFIRMATORY=NOT_EXECUTED; MERGE=HOLD", flush=True)
    if report["status"] != "RECOVERY_TWO_VARIANTS_AUDITED_DISCOVERY_UNADJUDICATED":
        raise SystemExit(2)

if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print("TTM_T5_V2_PRECHECK_OR_RECOVERY_HOLD:" +
              type(exc).__name__ + ":" + str(exc), file=sys.stderr)
        raise SystemExit(3)
