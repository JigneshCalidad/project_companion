"""Settings routes."""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from app.services.permissions import PermissionService


router = APIRouter(prefix="/api/settings", tags=["settings"])


class SettingsUpdate(BaseModel):
    enable_dynamic_scan: Optional[bool] = None
    read_only_mode: Optional[bool] = None


def get_permission_service() -> PermissionService:
    """Dependency to get permission service."""
    return PermissionService()


@router.get("")
async def get_settings(permission_service: PermissionService = Depends(get_permission_service)):
    """Get current settings."""
    return permission_service.get_settings()


@router.post("")
async def update_settings(
    settings: SettingsUpdate,
    permission_service: PermissionService = Depends(get_permission_service)
):
    """Update settings (with validation)."""
    update_dict = settings.dict(exclude_none=True)
    permission_service.update_settings(update_dict)
    return permission_service.get_settings()

