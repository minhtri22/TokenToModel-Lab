#!/usr/bin/env python3
"""A0D owner-local, read-only diagnostic for official EmbeddingGemma2 imports.

No download, installation, network, model initialization, training, or inference.
Only emits package paths, installed versions, and an exact import error summary.
"""
from __future__ import annotations

import importlib.metadata
import importlib.util
import json
import sys
import traceback

PACKAGES = ("torch", "transformers", "tokenizers", "huggingface_hub", "safetensors", "numpy")


def metadata_for(name: str) -> dict:
    item = {"name": name}
    try:
        item["version"] = importlib.metadata.version(name.replace("_", "-"))
    except importlib.metadata.PackageNotFoundError:
        item["version"] = None
    spec = importlib.util.find_spec(name)
    item["origin"] = spec.origin if spec else None
    return item


def run() -> dict:
    out = {
        "schema": "ttm.gemma2.a0d.owner_official_class_import_diagnostic.v1",
        "python_executable": sys.executable,
        "python_version": sys.version.split()[0],
        "python_is_312": sys.version_info[:2] == (3, 12),
        "packages": [metadata_for(x) for x in PACKAGES],
        "trained": False,
        "forward_called": False,
        "pretrained_weights_loaded": False,
    }
    if not out["python_is_312"]:
        out["status"] = "HOLD_PYTHON_NOT_312"
        return out
    for cls in ("AutoTokenizer", "EmbeddingGemma2TextConfig", "EmbeddingGemma2TextModel"):
        try:
            import transformers
            getattr(transformers, cls)
            out[cls] = "IMPORT_PASS"
        except Exception as exc:
            out[cls] = "IMPORT_FAIL"
            out["error_type"] = type(exc).__name__
            out["error_message"] = str(exc)[-1200:]
            out["exception_tail"] = traceback.format_exception_only(type(exc), exc)[-1].strip()[-1400:]
            out["status"] = "HOLD_OFFICIAL_CLASS_IMPORT_" + cls.upper()
            return out
    out["status"] = "PASS_IMPORT_ONLY_NO_INITIALIZATION"
    return out


if __name__ == "__main__":
    print(json.dumps(run(), ensure_ascii=False, sort_keys=True))
