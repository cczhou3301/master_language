"""
APIRouter declarations for backend–frontend API (from idl/api.yaml).
Prefix/tags declared here; route handlers are registered in app.api.*.
"""

from __future__ import annotations

from fastapi import APIRouter

# Each router name and prefix matches idl/api.yaml
auth_router = APIRouter(prefix="/auth", tags=["auth"])
user_router = APIRouter(prefix="/users", tags=["users"])
video_router = APIRouter(prefix="/videos", tags=["videos"])
