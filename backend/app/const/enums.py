"""
Enums for domain values stored as strings in DB (user.level, activation_code.status, etc.).
Use .value when comparing or persisting.
"""

from __future__ import annotations

from enum import StrEnum


class UserLevel(StrEnum):
    """User privilege level. Default for new users is FREE."""

    FREE = "free"
    PREMIUM = "premium"
    ADMIN = "admin"


class ActivationCodeStatus(StrEnum):
    """Activation code lifecycle."""

    UNUSED = "unused"
    USED = "used"
