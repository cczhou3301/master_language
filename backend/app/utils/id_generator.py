"""ID generator for BIGINT UNSIGNED primary keys."""
from __future__ import annotations

import uuid


def generate_bigint_id() -> int:
    """Generate a positive 64-bit id (BIGINT UNSIGNED). Use instead of auto-increment."""
    return uuid.uuid4().int % (2**64)


__all__ = ["generate_bigint_id"]
