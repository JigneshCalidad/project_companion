"""Service for querying the knowledge graph."""

from typing import Optional
from knowledge.store import KnowledgeStore


class GraphService:
    """Service for querying and exporting the knowledge graph."""
    
    def __init__(self, knowledge_store: KnowledgeStore):
        self.knowledge_store = knowledge_store
    
    def query(self, question: str) -> dict:
        """Query the knowledge graph with a natural language question."""
        return self.knowledge_store.query(question)
    
    def get_nodes(self, node_type: Optional[str] = None) -> list:
        """Get nodes from the graph."""
        return self.knowledge_store.get_nodes(node_type)
    
    def get_edges(self, edge_type: Optional[str] = None) -> list:
        """Get edges from the graph."""
        return self.knowledge_store.get_edges(edge_type)
    
    def export_json(self) -> dict:
        """Export graph as JSON."""
        return self.knowledge_store.export_json()
    
    def export_mermaid(self) -> str:
        """Export graph as Mermaid diagram."""
        return self.knowledge_store.export_mermaid()
    
    def get_statistics(self) -> dict:
        """Get graph statistics."""
        return self.knowledge_store.get_statistics()

