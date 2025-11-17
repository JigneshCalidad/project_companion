"""Static code scanner that orchestrates parsing and graph building."""

import os
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from scanner.file_indexer import index_directory
from scanner.parser_python import parse_file as parse_python
from scanner.parser_js import parse_file as parse_js
from scanner.parser_markdown import parse_file as parse_markdown
from scanner.schema import ScanResult, FileInfo, NodeType, EdgeType

logger = logging.getLogger(__name__)


def scan_repository(root_path: str) -> ScanResult:
    """Scan a repository and build a knowledge graph."""
    root_path = os.path.abspath(root_path)
    
    # Index all files
    files = index_directory(root_path)
    
    # Parse files based on language
    parsed_files = []
    for file_info in files:
        parsed = _parse_file_by_language(file_info)
        if parsed:
            parsed_files.append(parsed)
        else:
            # Keep file info even if not parsed
            parsed_files.append(file_info)
    
    # Build graph nodes and edges
    nodes, edges = _build_graph(parsed_files, root_path)
    
    # Collect metadata
    metadata = {
        "total_files": len(parsed_files),
        "languages": _count_languages(parsed_files),
        "total_symbols": sum(len(f.symbols) for f in parsed_files),
        "total_imports": sum(len(f.imports) for f in parsed_files),
    }
    
    return ScanResult(
        root_path=root_path,
        files=parsed_files,
        graph_nodes=nodes,
        graph_edges=edges,
        metadata=metadata
    )


def _parse_file_by_language(file_info: FileInfo) -> Optional[FileInfo]:
    """Parse a file based on its detected language."""
    if not file_info.language:
        return file_info
    
    try:
        if file_info.language == "python":
            return parse_python(file_info.path)
        elif file_info.language in ("javascript", "typescript"):
            return parse_js(file_info.path)
        elif file_info.language == "markdown":
            return parse_markdown(file_info.path)
    except Exception as e:
        # Log error but continue
        logger.warning(f"Error parsing {file_info.path}: {e}", exc_info=True)
        return file_info
    
    return file_info


def _build_graph(files: List[FileInfo], root_path: str) -> Tuple[List[Dict], List[Dict]]:
    """Build knowledge graph nodes and edges from parsed files."""
    nodes = []
    edges = []
    
    # Normalize root path for relative paths
    root = Path(root_path)
    
    # Create file nodes
    file_node_ids = {}
    for file_info in files:
        try:
            rel_path = str(Path(file_info.path).relative_to(root))
        except ValueError:
            # File is not under root, use absolute path as fallback
            logger.warning(f"File {file_info.path} is not under root {root_path}, using absolute path")
            rel_path = str(Path(file_info.path))
        node_id = f"file:{rel_path}"
        file_node_ids[file_info.path] = node_id
        
        nodes.append({
            "id": node_id,
            "type": NodeType.FILE,
            "label": Path(file_info.path).name,
            "path": rel_path,
            "language": file_info.language,
            "metadata": {
                "size": file_info.size,
                "line_count": file_info.line_count,
            }
        })
        
        # Create symbol nodes and edges
        for symbol in file_info.symbols:
            symbol_id = f"{node_id}:{symbol.type.value}:{symbol.name}"
            nodes.append({
                "id": symbol_id,
                "type": symbol.type,
                "label": symbol.name,
                "file_path": rel_path,
                "line_start": symbol.line_start,
                "line_end": symbol.line_end,
                "metadata": {
                    "docstring": symbol.docstring,
                    "signature": symbol.signature,
                    **(symbol.metadata or {})
                }
            })
            
            # Edge: file contains symbol
            edges.append({
                "source": node_id,
                "target": symbol_id,
                "type": EdgeType.CONTAINS,
                "metadata": {}
            })
        
        # Create import edges
        for imp in file_info.imports:
            # Try to resolve import to a file
            target_file = _resolve_import(imp, file_info.path, root_path)
            if target_file and target_file in file_node_ids:
                edges.append({
                    "source": node_id,
                    "target": file_node_ids[target_file],
                    "type": EdgeType.IMPORTS,
                    "metadata": {"import": imp}
                })
    
    # Create TODO nodes
    for file_info in files:
        if file_info.todos:
            try:
                rel_path = str(Path(file_info.path).relative_to(root))
            except ValueError:
                # File is not under root, use absolute path as fallback
                rel_path = str(Path(file_info.path))
            file_node_id = file_node_ids[file_info.path]
            
            for i, todo in enumerate(file_info.todos):
                todo_id = f"{file_node_id}:todo:{i}"
                nodes.append({
                    "id": todo_id,
                    "type": NodeType.TODO,
                    "label": todo[:50],  # Truncate for display
                    "file_path": rel_path,
                    "metadata": {"content": todo}
                })
                
                edges.append({
                    "source": file_node_id,
                    "target": todo_id,
                    "type": EdgeType.ASSOCIATED_WITH,
                    "metadata": {}
                })
    
    return nodes, edges


def _resolve_import(import_name: str, from_file: str, root_path: str) -> Optional[str]:
    """Try to resolve an import to an actual file path."""
    # Remove relative imports
    if import_name.startswith('.'):
        return None
    
    # Try common patterns
    from_path = Path(from_file).parent
    root = Path(root_path)
    
    # Try direct file match
    possible_paths = [
        from_path / f"{import_name}.py",
        from_path / import_name / "__init__.py",
        root / f"{import_name}.py",
        root / import_name / "__init__.py",
    ]
    
    # Try with path parts
    parts = import_name.split('.')
    if len(parts) > 1:
        # Use Path.joinpath for proper path construction
        possible_paths.extend([
            root / parts[0] / f"{parts[-1]}.py",
            root.joinpath(*parts[:-1]) / f"{parts[-1]}.py",
        ])
    
    for path in possible_paths:
        if path.exists() and path.is_file():
            return str(path)
    
    return None


def _count_languages(files: List[FileInfo]) -> Dict[str, int]:
    """Count files by language."""
    counts = {}
    for file_info in files:
        lang = file_info.language or "unknown"
        counts[lang] = counts.get(lang, 0) + 1
    return counts

