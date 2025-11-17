"""Knowledge graph storage using NetworkX and SQLite."""

import json
import sqlite3
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
import networkx as nx
from datetime import datetime


class KnowledgeStore:
    """Persistent storage for knowledge graphs."""
    
    def __init__(self, db_path: str = "knowledge/graph.db"):
        """Initialize the knowledge store."""
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.graph = nx.DiGraph()
        self._init_database()
        self._load_graph()
    
    def _init_database(self):
        """Initialize SQLite database schema."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Nodes table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS nodes (
                    id TEXT PRIMARY KEY,
                    type TEXT NOT NULL,
                    label TEXT NOT NULL,
                    data TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Edges table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS edges (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    source TEXT NOT NULL,
                    target TEXT NOT NULL,
                    type TEXT NOT NULL,
                    data TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (source) REFERENCES nodes(id),
                    FOREIGN KEY (target) REFERENCES nodes(id)
                )
            """)
            
            # Scans table (track scan history)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS scans (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    root_path TEXT NOT NULL,
                    metadata TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.commit()
    
    def _load_graph(self):
        """Load graph from database into NetworkX."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Load nodes
            cursor.execute("SELECT id, type, label, data FROM nodes")
            for row in cursor.fetchall():
                node_id, node_type, label, data_json = row
                data = json.loads(data_json)
                self.graph.add_node(node_id, type=node_type, label=label, **data)
            
            # Load edges
            cursor.execute("SELECT source, target, type, data FROM edges")
            for row in cursor.fetchall():
                source, target, edge_type, data_json = row
                data = json.loads(data_json) if data_json else {}
                self.graph.add_edge(source, target, type=edge_type, **data)
    
    def add_scan(self, scan_result) -> int:
        """Add a scan result to the knowledge graph."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Record scan
            metadata_json = json.dumps(scan_result.metadata)
            cursor.execute(
                "INSERT INTO scans (root_path, metadata) VALUES (?, ?)",
                (scan_result.root_path, metadata_json)
            )
            scan_id = cursor.lastrowid
            
            # Add nodes
            for node in scan_result.graph_nodes:
                node_id = node["id"]
                node_data = {k: v for k, v in node.items() if k != "id"}
                node_data_json = json.dumps(node_data)
                
                cursor.execute("""
                    INSERT OR REPLACE INTO nodes (id, type, label, data, updated_at)
                    VALUES (?, ?, ?, ?, ?)
                """, (node_id, node["type"], node["label"], node_data_json, datetime.now()))
                
                # Update NetworkX graph
                self.graph.add_node(node_id, **node_data)
            
            # Add edges
            for edge in scan_result.graph_edges:
                edge_data = {k: v for k, v in edge.items() if k not in ("source", "target")}
                edge_data_json = json.dumps(edge_data) if edge_data else None
                
                cursor.execute("""
                    INSERT INTO edges (source, target, type, data)
                    VALUES (?, ?, ?, ?)
                """, (edge["source"], edge["target"], edge["type"], edge_data_json))
                
                # Update NetworkX graph
                self.graph.add_edge(edge["source"], edge["target"], **edge_data)
            
            conn.commit()
        
        return scan_id
    
    def get_nodes(self, node_type: Optional[str] = None) -> List[Dict]:
        """Get all nodes, optionally filtered by type."""
        nodes = []
        for node_id, data in self.graph.nodes(data=True):
            if node_type is None or data.get("type") == node_type:
                nodes.append({
                    "id": node_id,
                    **data
                })
        return nodes
    
    def get_edges(self, edge_type: Optional[str] = None) -> List[Dict]:
        """Get all edges, optionally filtered by type."""
        edges = []
        for source, target, data in self.graph.edges(data=True):
            if edge_type is None or data.get("type") == edge_type:
                edges.append({
                    "source": source,
                    "target": target,
                    **data
                })
        return edges
    
    def query(self, question: str) -> Dict[str, Any]:
        """Query the knowledge graph (simplified - can be enhanced with embeddings)."""
        # Simple keyword-based search
        question_lower = question.lower()
        keywords = question_lower.split()
        
        matching_nodes = []
        for node_id, data in self.graph.nodes(data=True):
            label = str(data.get("label", "")).lower()
            node_type = str(data.get("type", "")).lower()
            
            # Check if any keyword matches
            if any(kw in label or kw in node_type for kw in keywords if len(kw) > 2):
                matching_nodes.append({
                    "id": node_id,
                    **data
                })
        
        # Find related nodes
        related_nodes = set()
        for node in matching_nodes[:10]:  # Limit to top 10
            node_id = node["id"]
            # Get neighbors
            for neighbor in self.graph.neighbors(node_id):
                related_nodes.add(neighbor)
        
        related_data = []
        for node_id in list(related_nodes)[:20]:  # Limit related nodes
            if node_id in self.graph:
                related_data.append({
                    "id": node_id,
                    **self.graph.nodes[node_id]
                })
        
        return {
            "question": question,
            "matches": matching_nodes[:20],
            "related": related_data,
            "total_matches": len(matching_nodes)
        }
    
    def export_json(self) -> Dict:
        """Export graph as JSON."""
        nodes = []
        for node_id, data in self.graph.nodes(data=True):
            nodes.append({
                "id": node_id,
                **data
            })
        
        edges = []
        for source, target, data in self.graph.edges(data=True):
            edges.append({
                "source": source,
                "target": target,
                **data
            })
        
        return {
            "nodes": nodes,
            "edges": edges,
            "metadata": {
                "node_count": len(nodes),
                "edge_count": len(edges)
            }
        }
    
    def export_mermaid(self) -> str:
        """Export graph as Mermaid diagram."""
        lines = ["graph TD"]
        
        # Add nodes
        for node_id, data in self.graph.nodes(data=True):
            label = data.get("label", node_id)
            node_type = data.get("type", "unknown")
            # Escape special characters
            label = label.replace('"', '\\"')
            lines.append(f'    {node_id}["{label} ({node_type})"]')
        
        # Add edges (limit to avoid huge diagrams)
        edge_count = 0
        for source, target, data in self.graph.edges(data=True):
            if edge_count > 100:  # Limit edges for readability
                lines.append("    %% ... more edges ...")
                break
            edge_type = data.get("type", "")
            lines.append(f"    {source} -->|{edge_type}| {target}")
            edge_count += 1
        
        return "\n".join(lines)
    
    def get_statistics(self) -> Dict:
        """Get graph statistics."""
        return {
            "node_count": self.graph.number_of_nodes(),
            "edge_count": self.graph.number_of_edges(),
            "is_connected": nx.is_weakly_connected(self.graph),
            "components": nx.number_weakly_connected_components(self.graph),
        }

