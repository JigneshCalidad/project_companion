"""Tests for knowledge graph."""

import pytest
from pathlib import Path
from knowledge.store import KnowledgeStore
from scanner.static_scanner import scan_repository


def test_knowledge_store():
    """Test knowledge store operations."""
    # Use a test database
    store = KnowledgeStore(db_path=":memory:")
    
    # Scan sample repo
    repo_path = Path(__file__).parent.parent / "examples" / "sample_repo"
    scan_result = scan_repository(str(repo_path))
    
    # Add scan
    scan_id = store.add_scan(scan_result)
    assert scan_id > 0
    
    # Get nodes
    nodes = store.get_nodes()
    assert len(nodes) > 0
    
    # Get edges
    edges = store.get_edges()
    assert len(edges) > 0
    
    # Query
    result = store.query("calculator")
    assert result["total_matches"] > 0
    
    # Export
    json_data = store.export_json()
    assert "nodes" in json_data
    assert "edges" in json_data
    
    mermaid = store.export_mermaid()
    assert "graph" in mermaid.lower()
    
    # Statistics
    stats = store.get_statistics()
    assert "node_count" in stats
    assert "edge_count" in stats

