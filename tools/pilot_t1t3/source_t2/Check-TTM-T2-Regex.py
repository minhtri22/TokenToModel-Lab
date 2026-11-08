#!/usr/bin/env python3
"""Read-only dependency check. Exit 3 means only pinned regex wheel is missing."""
import sys
if sys.version_info[:2] != (3,13):
    print('TTM_F32_PYTHON_UNEXPECTED_VERSION='+sys.version.split()[0]);sys.exit(4)
try:
    import regex
except ImportError:
    print('TTM_F32_REGEX=NOT_INSTALLED');sys.exit(3)
if regex.__version__ != '2026.5.9':
    print('TTM_F32_REGEX=WRONG_VERSION:'+regex.__version__);sys.exit(4)
print('TTM_F32_REGEX=PINNED_PASS:'+regex.__version__)
sys.exit(0)
