"""F0 write broker contract. No file-writing implementation in I0A-S."""
from __future__ import annotations
from dataclasses import dataclass

MAX_BYTES = 2 * 1024**3


class BrokerUnavailable(PermissionError):
    pass


@dataclass(frozen=True)
class BrokerPolicy:
    workspace_root: str
    quota_bytes: int = MAX_BYTES
    create_new_only: bool = True
    prohibit_reparse: bool = True
    require_restricted_worker: bool = True


def write_file(*_args: object, **_kwargs: object) -> None:
    """Must never be a passthrough to open(), nor a post-hoc quota check."""
    raise BrokerUnavailable("QA0_WRITE_BROKER_UNIMPLEMENTED")
