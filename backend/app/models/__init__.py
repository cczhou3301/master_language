"""Models: generated from DB by scripts/gen_models_from_db.py. One file per table."""
from __future__ import annotations

from app.utils.id_generator import generate_bigint_id
from .base import Base

from .user import User
from .video import Video
from .activation_code import ActivationCode
from .subtitle_line import SubtitleLine
from .user_device import UserDevice
from .user_sentence import UserSentence
from .user_vocabulary import UserVocabulary

__all__ = [
    "Base",
    "generate_bigint_id",
    "User",
    "Video",
    "ActivationCode",
    "SubtitleLine",
    "UserDevice",
    "UserSentence",
    "UserVocabulary",
]
