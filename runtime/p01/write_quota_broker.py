"""P01 Write Broker: strict pure policy/quota planner; actual writes DENIED.

The quota ledger can be independently tested without I/O. It is NOT a secure
file-writing broker until a restricted worker and handle-relative Windows
create-new/no-reparse design have been qualified on the target machine.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import PureWindowsPath
import re

MAX_BYTES = 2 * 1024**3
_RESERVED = frozenset(
    ("CON", "PRN", "AUX", "NUL")
    + tuple(f"COM{i}" for i in range(1, 10))
    + tuple(f"LPT{i}" for i in range(1, 10))
)
_NAME_PATTERN = re.compile(r"^[^<>:\"/\\|?*\x00-\x1f]+$")


class BrokerUnavailable(PermissionError):
    pass


@dataclass(frozen=True)
class BrokerPolicy:
    workspace_root: str
    quota_bytes: int = MAX_BYTES
    create_new_only: bool = True
    prohibit_reparse: bool = True
    require_restricted_worker: bool = True

    def validate(self) -> None:
        root = self.workspace_root
        if (type(root) is not str or not root
                or not PureWindowsPath(root).is_absolute()
                or not re.match(r"^[A-Za-z]:\\", root)
                or root.endswith(("\\", "/", ".", " "))
                or type(self.quota_bytes) is not int
                or not (0 < self.quota_bytes <= MAX_BYTES)
                or self.create_new_only is not True
                or self.prohibit_reparse is not True
                or self.require_restricted_worker is not True):
            raise BrokerUnavailable("BROKER_POLICY_UNSAFE")


def relative_output_path(path: str) -> str:
    """Reject escape, ADS, UNC, device names, ambiguous and alias paths."""
    if type(path) is not str or not path:
        raise BrokerUnavailable("OUTPUT_PATH_INVALID")
    if "\\" in path or path.startswith("/") or "//" in path:
        raise BrokerUnavailable("OUTPUT_PATH_NONCANONICAL")
    candidate = PureWindowsPath(path)
    if candidate.drive or candidate.root:
        raise BrokerUnavailable("OUTPUT_PATH_ABSOLUTE_OR_UNC")
    parts = path.split("/")
    if not all(parts) or any(x in (".", "..") for x in parts):
        raise BrokerUnavailable("OUTPUT_PATH_TRAVERSAL")
    for part in parts:
        if (part.endswith((".", " "))
                or not _NAME_PATTERN.fullmatch(part)
                or part.split(".")[0].upper() in _RESERVED):
            raise BrokerUnavailable("OUTPUT_PATH_AMBIGUOUS")
    if len(path) > 240:
        raise BrokerUnavailable("OUTPUT_PATH_TOO_LONG")
    return "/".join(parts)


@dataclass
class QuotaLedger:
    """A dry-run deterministic pre-write policy; not a filesystem writer."""
    policy: BrokerPolicy
    reserved_bytes: int = 0
    reserved_paths: set[str] = field(default_factory=set)

    def __post_init__(self) -> None:
        if type(self.policy) is not BrokerPolicy:
            raise BrokerUnavailable("BROKER_POLICY_TYPE")
        self.policy.validate()
        if type(self.reserved_bytes) is not int or self.reserved_bytes != 0:
            raise BrokerUnavailable("QUOTA_LEDGER_MUST_START_EMPTY")
        if self.reserved_paths:
            raise BrokerUnavailable("QUOTA_LEDGER_MUST_START_EMPTY")

    def reserve(self, path: str, size: int) -> str:
        relative = relative_output_path(path)
        if type(size) is not int or not (0 <= size <= self.policy.quota_bytes):
            raise BrokerUnavailable("OUTPUT_SIZE_INVALID")
        key = relative.casefold()
        if key in self.reserved_paths:
            raise BrokerUnavailable("CREATE_NEW_ONLY_COLLISION")
        if self.reserved_bytes + size > self.policy.quota_bytes:
            raise BrokerUnavailable("QUOTA_EXCEEDED_BEFORE_WRITE")
        self.reserved_paths.add(key)
        self.reserved_bytes += size
        return relative


def write_file(*_args: object, **_kwargs: object) -> None:
    # No direct call to open()/CreateFile in this unqualified implementation.
    # Dry-run reservation does not attest ACL, reparse or broker exclusivity.
    raise BrokerUnavailable("QA0_OS_RESTRICTED_WRITE_BROKER_NOT_QUALIFIED")
