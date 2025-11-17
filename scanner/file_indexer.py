"""File indexer that walks directories and identifies file types."""

import os
from pathlib import Path
from typing import List, Set, Optional
from scanner.schema import FileInfo


# File extensions mapped to languages
LANGUAGE_EXTENSIONS = {
    'python': {'.py', '.pyw', '.pyi'},
    'javascript': {'.js', '.mjs', '.cjs'},
    'typescript': {'.ts', '.tsx'},
    'markdown': {'.md', '.markdown', '.mdown'},
    'yaml': {'.yaml', '.yml'},
    'json': {'.json'},
    'html': {'.html', '.htm'},
    'css': {'.css', '.scss', '.sass'},
    'rust': {'.rs'},
    'go': {'.go'},
    'java': {'.java'},
    'cpp': {'.cpp', '.cc', '.cxx', '.hpp', '.h'},
    'c': {'.c', '.h'},
}


# Directories to ignore
IGNORE_DIRS = {
    '.git', '.svn', '.hg', '.bzr',
    '__pycache__', 'node_modules', '.venv', 'venv', 'env',
    '.pytest_cache', '.mypy_cache', '.ruff_cache',
    'dist', 'build', '.next', '.nuxt', '.cache',
    'coverage', '.coverage', 'htmlcov',
}


# Files to ignore
IGNORE_FILES = {
    '.DS_Store', 'Thumbs.db', '.gitkeep',
}


def detect_language(file_path: str) -> Optional[str]:
    """Detect programming language from file extension."""
    ext = Path(file_path).suffix.lower()
    for lang, extensions in LANGUAGE_EXTENSIONS.items():
        if ext in extensions:
            return lang
    return None


def should_ignore(path: str) -> bool:
    """Check if a path should be ignored."""
    path_obj = Path(path)
    
    # Check if any parent directory is ignored
    for part in path_obj.parts:
        if part in IGNORE_DIRS:
            return True
    
    # Check if file itself is ignored
    if path_obj.name in IGNORE_FILES:
        return True
    
    return False


def index_directory(root_path: str, max_depth: int = 100) -> List[FileInfo]:
    """Walk a directory and create FileInfo objects for all files."""
    files = []
    root = Path(root_path).resolve()
    
    if not root.exists() or not root.is_dir():
        return files
    
    for file_path in root.rglob('*'):
        if should_ignore(str(file_path)):
            continue
        
        if not file_path.is_file():
            continue
        
        # Check depth
        depth = len(file_path.relative_to(root).parts)
        if depth > max_depth:
            continue
        
        language = detect_language(str(file_path))
        
        file_info = FileInfo(
            path=str(file_path),
            language=language
        )
        
        try:
            file_info.size = file_path.stat().st_size
            # Count lines efficiently by reading as text with error handling
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                file_info.line_count = sum(1 for _ in f)
        except (OSError, IOError):
            pass
        
        files.append(file_info)
    
    return files

