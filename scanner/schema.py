"""Schema definitions for scanner data structures."""

from dataclasses import dataclass
from typing import Dict, List, Optional, Set
from enum import Enum


class NodeType(str, Enum):
    """Types of nodes in the knowledge graph."""
    FILE = "file"
    FUNCTION = "function"
    CLASS = "class"
    VARIABLE = "variable"
    MODULE = "module"
    HEADING = "heading"
    TODO = "todo"
    IMPORT = "import"
    COMMENT = "comment"


class EdgeType(str, Enum):
    """Types of edges in the knowledge graph."""
    IMPORTS = "imports"
    CALLS = "calls"
    DEFINES = "defines"
    REFERENCES = "references"
    CONTAINS = "contains"
    ASSOCIATED_WITH = "associated_with"


@dataclass
class Symbol:
    """Represents a code symbol (function, class, variable, etc.)."""
    name: str
    type: NodeType
    file_path: str
    line_start: int
    line_end: int
    docstring: Optional[str] = None
    signature: Optional[str] = None
    metadata: Optional[Dict] = None


@dataclass
class FileInfo:
    """Represents information about a file."""
    path: str
    language: Optional[str] = None
    size: int = 0
    line_count: int = 0
    symbols: List[Symbol] = None
    imports: List[str] = None
    todos: List[str] = None
    
    def __post_init__(self):
        if self.symbols is None:
            self.symbols = []
        if self.imports is None:
            self.imports = []
        if self.todos is None:
            self.todos = []


@dataclass
class ScanResult:
    """Result of scanning a repository."""
    root_path: str
    files: List[FileInfo]
    graph_nodes: List[Dict]
    graph_edges: List[Dict]
    metadata: Dict
    
    def __post_init__(self):
        if self.files is None:
            self.files = []
        if self.graph_nodes is None:
            self.graph_nodes = []
        if self.graph_edges is None:
            self.graph_edges = []
        if self.metadata is None:
            self.metadata = {}

