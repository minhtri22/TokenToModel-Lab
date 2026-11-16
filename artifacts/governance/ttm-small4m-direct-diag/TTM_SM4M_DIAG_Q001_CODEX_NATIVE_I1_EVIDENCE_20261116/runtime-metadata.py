from importlib.metadata import PackageNotFoundError, version
import json
import os
import platform
import sys

packages = {}
for name in ("cryptography", "psutil", "torch"):
    try:
        packages[name] = version(name)
    except PackageNotFoundError:
        packages[name] = None
print(json.dumps({"python": sys.executable, "cpu": platform.processor(),
                  "arch": platform.machine(), "logical_cpu_count": os.cpu_count(),
                  "installed_distribution_metadata_only": packages,
                  "torch_imported": "torch" in sys.modules}, indent=2))
