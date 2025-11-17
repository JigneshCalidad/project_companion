"""Scan routes."""

import logging
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
from app.services.scan_service import ScanService
from app.services.permissions import PermissionService

logger = logging.getLogger(__name__)


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
    knowledge_store = None,  # Will be injected
    permission_service: PermissionService = None  # Will be injected
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
    except FileNotFoundError as e:
        logger.warning(f"Path not found: {request.path}")
        raise HTTPException(status_code=404, detail=f"Path not found: {request.path}")
    except PermissionError as e:
        logger.warning(f"Permission denied for path: {request.path}")
        raise HTTPException(status_code=403, detail="Permission denied to access this path")
    except Exception as e:
        logger.error(f"Error scanning repository: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to scan repository. Please check the path and try again.")


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
        logger.warning(f"Permission denied for dynamic scan: {request.url}")
        raise HTTPException(status_code=403, detail="Dynamic scanning is not enabled or permission denied")
    except Exception as e:
        logger.error(f"Error performing dynamic scan: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to perform dynamic scan. Please try again.")

