#!/usr/bin/env python3
"""Read-only exact V8 science space gate diagnostics. Never executes training.

No file or directory creation. No secret reads. No TRAIN/VAL/TEST access.
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
from pathlib import Path

TWO_GIB = 2 * 1024 ** 3
ROOT = "/content/drive/MyDrive/TTM/ttm-small-pilot/ttm_small4m_ac_objective_only_v1"
SCIENCE = "TTM_SMALL4M_AC_OBJECTIVE_ONLY_V1_SCIENCE"


def stat(label, path):
    p = Path(path)
    data = {"name": label, "path": str(p), "exists": p.exists(),
            "is_dir": p.is_dir(), "is_symlink": p.is_symlink()}
    if p.is_dir():
        usage = shutil.disk_usage(p)
        data.update({"total_bytes": usage.total, "used_bytes": usage.used,
                     "free_bytes": usage.free, "free_gib": round(usage.free / 1024 ** 3, 4),
                     "meets_runner_2_gib_gate": usage.free >= TWO_GIB})
        vfs = os.statvfs(p)
        data.update({"f_bavail": vfs.f_bavail, "f_frsize": vfs.f_frsize})
    return data


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--owner", default=ROOT)
    a = p.parse_args()
    owner = Path(a.owner)
    science = owner / SCIENCE
    results = [stat("OWNER_DRIVE", owner),
               stat("COLAB_CONTENT", "/content"),
               stat("COLAB_TMP", "/tmp")]
    owner_info = results[0]
    gate = owner_info.get("meets_runner_2_gib_gate")
    status = ("PASS_EXACT_V8_DISK_GATE" if gate is True else
              "HOLD_DRIVE_PARENT_FREE_BELOW_2_GIB" if gate is False else
              "HOLD_OWNER_DRIVE_PATH_INVALID")
    report = {
        "schema": "ttm.small4m.ac.v8.read_only_disk_guard_probe.v1",
        "status": status,
        "exact_runner_guard": "root.parent.is_dir() and shutil.disk_usage(root.parent).free >= 2 * 1024**3",
        "required_free_bytes": TWO_GIB,
        "read_only": True,
        "created_or_deleted_any_file": False,
        "science_output_path_exists": science.exists(),
        "science_output_is_symlink": science.is_symlink(),
        "measurements": results,
        "science_steps_performed_by_this_probe": 0,
        "scope": "filesystem_and_mount_space_only_not_Google_Drive_API_storageQuota"
    }
    print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
