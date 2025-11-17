"""Service for scanning repositories."""

from typing import Optional
from scanner.static_scanner import scan_repository
from scanner.dynamic_scanner import DynamicScanner
from knowledge.store import KnowledgeStore
from app.services.permissions import PermissionService


class ScanService:
    """Service for orchestrating scans."""
    
    def __init__(self, knowledge_store: KnowledgeStore, permission_service: PermissionService):
        self.knowledge_store = knowledge_store
        self.permission_service = permission_service
        self.dynamic_scanner = DynamicScanner(enabled=False)
    
    def scan_static(self, path: str) -> dict:
        """Perform a static scan of a repository."""
        scan_result = scan_repository(path)
        scan_id = self.knowledge_store.add_scan(scan_result)
        
        return {
            "scan_id": scan_id,
            "root_path": scan_result.root_path,
            "metadata": scan_result.metadata,
            "nodes_added": len(scan_result.graph_nodes),
            "edges_added": len(scan_result.graph_edges)
        }
    
    async def scan_dynamic(self, url: str) -> dict:
        """Perform a dynamic scan of a web application."""
        if not self.permission_service.can_use_dynamic_scan():
            raise PermissionError("Dynamic scanning is not enabled. Enable in settings first.")
        
        self.dynamic_scanner.enabled = True
        try:
            result = await self.dynamic_scanner.scan_url(url)
            return {
                "url": url,
                "result": result
            }
        finally:
            self.dynamic_scanner.enabled = False

