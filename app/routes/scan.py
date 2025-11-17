"""Scan routes."""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.services.permissions import PermissionService
from app.services.scan_service import ScanService
from knowledge.store import KnowledgeStore


router = APIRouter(prefix="/api/scan", tags=["scan"])


class ScanRequest(BaseModel):
    path: str
    dynamic: bool = False
    url: Optional[str] = None


class ScanResponse(BaseModel):
    scan_id: int
    root_path: str
    metadata: dict
    nodes_added: int
    edges_added: int


def get_scan_service() -> ScanService:
    """Dependency to get scan service."""
    knowledge_store = KnowledgeStore()
    permission_service = PermissionService()
    return ScanService(knowledge_store, permission_service)


@router.post("/static", response_model=ScanResponse)
async def scan_static(
    request: ScanRequest, scan_service: ScanService = Depends(get_scan_service)
):
    """Perform a static scan of a repository."""
    try:
        result = scan_service.scan_static(request.path)
        return ScanResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/dynamic")
async def scan_dynamic(
    request: ScanRequest, scan_service: ScanService = Depends(get_scan_service)
):
    """Perform a dynamic scan of a web application."""
    if not request.url:
        raise HTTPException(status_code=400, detail="URL is required for dynamic scan")

    try:
        result = await scan_service.scan_dynamic(request.url)
        return result
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

