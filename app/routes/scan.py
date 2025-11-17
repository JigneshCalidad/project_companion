"""Scan routes."""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
from app.services.scan_service import ScanService
from app.services.permissions import PermissionService


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


def get_scan_service(
    knowledge_store: Optional[object] = None,  # Will be injected
    permission_service: Optional[PermissionService] = None  # Will be injected
) -> ScanService:
    """Dependency to get scan service."""
    # This will be properly injected in main.py
    from knowledge.store import KnowledgeStore
    if knowledge_store is None:
        knowledge_store = KnowledgeStore()
    if permission_service is None:
        permission_service = PermissionService()
    return ScanService(knowledge_store, permission_service)


@router.post("/static", response_model=ScanResponse)
async def scan_static(
    request: ScanRequest,
    scan_service: ScanService = Depends(get_scan_service)
):
    """Perform a static scan of a repository."""
    try:
        result = scan_service.scan_static(request.path)
        return ScanResponse(**result)
    except (ValueError, FileNotFoundError, PermissionError) as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post("/dynamic")
async def scan_dynamic(
    request: ScanRequest,
    scan_service: ScanService = Depends(get_scan_service)
):
    """Perform a dynamic scan of a web application."""
    if not request.url:
        raise HTTPException(status_code=400, detail="URL is required for dynamic scan")
    
    try:
        result = await scan_service.scan_dynamic(request.url)
        return result
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except (ValueError, RuntimeError) as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

