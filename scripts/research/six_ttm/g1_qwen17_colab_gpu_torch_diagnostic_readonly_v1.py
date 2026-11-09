#!/usr/bin/env python3
"""G1 target17: READ-ONLY Colab GPU/Torch environment diagnostic.

No writes, no model/dataset access, no weight download, no pip install.
A diagnostic PASS does NOT replace the frozen technical preflight or science review.
"""
from __future__ import annotations
import importlib.metadata
import json
import platform
import shutil
import subprocess
import sys

PIN = "2.14.1+cu130"
EXPECTED_GPU = "T4"

def main():
    out = {
        "schema": "ttm.six.g1.target17.cuda_environment_diagnostic.v1",
        "scope": "READONLY_ENVIRONMENT_ONLY",
        "python": platform.python_version(),
        "python_executable": sys.executable,
        "expected_torch": PIN,
        "science_executed": False,
        "weights_downloaded": False,
        "model_loaded": False,
        "data_read": False,
        "files_written_by_script": False,
        "one_shot_consumed": False,
    }
    exe = shutil.which("nvidia-smi")
    out["nvidia_smi_present"] = bool(exe)
    if exe:
        try:
            p = subprocess.run(
                [exe, "--query-gpu=name,driver_version,memory.total,memory.free",
                 "--format=csv,noheader,nounits"],
                capture_output=True, text=True, timeout=15, check=False,
            )
            out["nvidia_smi_exit"] = p.returncode
            if p.returncode == 0:
                lines = [x.strip() for x in p.stdout.splitlines() if x.strip()]
                out["nvidia_smi_gpu_rows"] = lines[:4]
            else:
                out["nvidia_smi_error"] = p.stderr.strip()[:400]
        except (OSError, subprocess.TimeoutExpired) as exc:
            out["nvidia_smi_error"] = type(exc).__name__
    try:
        import torch
        out["torch"] = str(torch.__version__)
        out["torch_cuda_compiled"] = torch.version.cuda
        out["torch_cuda_available"] = bool(torch.cuda.is_available())
        if out["torch_cuda_available"]:
            out["torch_device_name"] = str(torch.cuda.get_device_name(0))
            out["torch_compute_capability"] = list(torch.cuda.get_device_capability(0))
    except Exception as exc:
        out["torch_import_error_type"] = type(exc).__name__
        out["torch_import_error"] = str(exc)[:400]
    try:
        out["installed_torch_distribution"] = importlib.metadata.version("torch")
    except importlib.metadata.PackageNotFoundError:
        out["installed_torch_distribution"] = None
    gpu_rows = out.get("nvidia_smi_gpu_rows", [])
    has_t4 = any(EXPECTED_GPU.lower() in row.lower() for row in gpu_rows)
    if not has_t4:
        out["status"] = "STOP_T4_NOT_CONFIRMED_CHECK_COLAB_GPU_RUNTIME"
    elif out.get("torch") != PIN:
        out["status"] = "STOP_T4_PRESENT_PINNED_CUDA_TORCH_NOT_LOADED"
    elif not out.get("torch_cuda_available", False):
        out["status"] = "STOP_T4_PRESENT_TORCH_CUDA_RUNTIME_UNAVAILABLE"
    elif out.get("torch_compute_capability") != [7, 5]:
        out["status"] = "STOP_GPU_COMPUTE_CAPABILITY_NOT_75"
    else:
        out["status"] = "PASS_GPU_TORCH_DIAGNOSTIC_ONLY_REQUIRES_ORIGINAL_PREFLIGHT"
    print("G1_TARGET17_GPU_DIAGNOSTIC=" + json.dumps(out, sort_keys=True))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
