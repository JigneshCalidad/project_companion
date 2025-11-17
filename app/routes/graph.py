"""Graph routes."""

from fastapi import APIRouter, Depends
from typing import Optional
from app.services.graph_service import GraphService


router = APIRouter(prefix="/api/graph", tags=["graph"])


def get_graph_service(knowledge_store=None) -> GraphService:
    """Dependency to get graph service."""
    from knowledge.store import KnowledgeStore
    if knowledge_store is None:
        knowledge_store = KnowledgeStore()
    return GraphService(knowledge_store)


@router.get("/nodes")
async def get_nodes(
    node_type: Optional[str] = None,
    graph_service: GraphService = Depends(get_graph_service)
):
    """Get all nodes from the knowledge graph."""
    return graph_service.get_nodes(node_type)


@router.get("/edges")
async def get_edges(
    edge_type: Optional[str] = None,
    graph_service: GraphService = Depends(get_graph_service)
):
    """Get all edges from the knowledge graph."""
    return graph_service.get_edges(edge_type)


@router.get("/export/json")
async def export_json(graph_service: GraphService = Depends(get_graph_service)):
    """Export graph as JSON."""
    return graph_service.export_json()


@router.get("/export/mermaid")
async def export_mermaid(graph_service: GraphService = Depends(get_graph_service)):
    """Export graph as Mermaid diagram."""
    return {"mermaid": graph_service.export_mermaid()}


@router.get("/statistics")
async def get_statistics(graph_service: GraphService = Depends(get_graph_service)):
    """Get graph statistics."""
    return graph_service.get_statistics()

