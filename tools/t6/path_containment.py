"""Fail-closed T6 artifacts/qa/t6 path confinement (including Windows junctions).

Static developer-worktree guard, not an atomic protection against a concurrent
attacker replacing filesystem components between checks and open().
Does not create directories, follow reparse points, or modify source/TEST.
"""
from __future__ import annotations

import os
import re
import stat
from pathlib import Path

_SEGMENT = re.compile(r"^[A-Za-z0-9_.-]+$")
_RESERVED = {"CON", "PRN", "AUX", "NUL", *(f"COM{i}" for i in range(1, 10)),
             *(f"LPT{i}" for i in range(1, 10))}
_REPARSE = getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0)


def _within(child: Path, parent: Path) -> bool:
    try:
        child.relative_to(parent)
        return True
    except ValueError:
        return False


def _reparse(path: Path) -> bool:
    """Reject all supported links/reparse points, including Windows junctions."""
    if path.is_symlink():
        return True
    is_junction = getattr(path, "is_junction", None)  # introduced in Python 3.12
    if is_junction is not None and is_junction():
        return True
    try:
        flags = getattr(path.lstat(), "st_file_attributes", 0)
    except FileNotFoundError:
        return False
    return bool(_REPARSE and flags & _REPARSE)


def resolve_t6_artifact(
    root: Path,
    relative: str,
    *,
    for_write: bool,
    suffix: str,
) -> Path:
    """Validate a T6 file without creating directories or opening it.

    Only forward-slash, repo-relative artifacts/qa/t6 paths are accepted.
    Existing ancestors and the leaf may not be symlinks or Windows reparse
    points. The resolved path must remain in the resolved T6 artifact subtree.

    Caller must use exclusive creation (open('x')) for a write; a concurrent
    hostile path swap is outside the single-user fixture threat model.
    """
    if not isinstance(relative, str) or not relative or "\\" in relative or "\x00" in relative:
        raise ValueError("T6_PATH_INVALID_RELATIVE")
    if relative.startswith("/") or re.match(r"^[A-Za-z]:", relative):
        raise ValueError("T6_PATH_ABSOLUTE_OR_DRIVE")
    parts = relative.split("/")
    if (
        len(parts) < 4 or parts[:3] != ["artifacts", "qa", "t6"]
        or any(not part or part in {".", ".."} or not _SEGMENT.fullmatch(part)
               or part.split(".")[0].upper() in _RESERVED for part in parts)
        or not parts[-1].endswith(suffix)
    ):
        raise ValueError("T6_PATH_OUTSIDE_SCOPED_SUBTREE")

    logical_root = Path(root).absolute()
    if not logical_root.is_dir() or _reparse(logical_root):
        raise ValueError("T6_ROOT_INVALID_OR_REPARSE")
    actual_root = logical_root.resolve(strict=True)
    if os.path.normcase(str(logical_root)) != os.path.normcase(str(actual_root)):
        raise ValueError("T6_ROOT_REDIRECTED")

    base = actual_root / "artifacts" / "qa" / "t6"
    dest = actual_root.joinpath(*parts)
    if not _within(dest, base):
        raise ValueError("T6_PATH_OUTSIDE_SCOPED_SUBTREE")

    for idx in range(1, len(parts) + 1):
        component = actual_root.joinpath(*parts[:idx])
        if _reparse(component):
            raise ValueError("T6_REPARSE_POINT_DENIED")
        # strict=False lets us validate a not-yet-created output leaf.
        # It also resolves any ancestor that the lstat checks could have missed.
        if not _within(component.resolve(strict=False), base) and idx >= 3:
            raise ValueError("T6_RESOLVED_PATH_ESCAPES_SUBTREE")

    if for_write:
        if not dest.parent.is_dir():
            raise ValueError("T6_OUTPUT_PARENT_MUST_EXIST")
        if dest.exists() or dest.is_symlink():
            raise FileExistsError("T6_OUTPUT_ALREADY_EXISTS_NO_OVERWRITE")
    else:
        if not dest.is_file():
            raise ValueError("T6_INPUT_MUST_BE_EXISTING_FILE")
    return dest
