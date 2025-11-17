"""Markdown file parser for extracting structure and headings."""

import re
from typing import List, Optional
from scanner.schema import Symbol, NodeType, FileInfo


def parse_file(file_path: str) -> Optional[FileInfo]:
    """Parse a Markdown file and extract headings and structure."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except UnicodeDecodeError:
        return None
    
    file_info = FileInfo(
        path=file_path,
        language="markdown",
        size=len(content),
        line_count=len(content.splitlines())
    )
    
    # Extract headings
    headings = _extract_headings(content, file_path)
    file_info.symbols.extend(headings)
    
    # Extract TODOs
    todos = _extract_todos(content)
    file_info.todos = todos
    
    return file_info


def _extract_headings(content: str, file_path: str) -> List[Symbol]:
    """Extract markdown headings."""
    headings = []
    lines = content.splitlines()
    
    for i, line in enumerate(lines, start=1):
        # Match ATX headings: # Heading
        match = re.match(r'^(#{1,6})\s+(.+)$', line)
        if match:
            level = len(match.group(1))
            heading_text = match.group(2).strip()
            
            symbol = Symbol(
                name=heading_text,
                type=NodeType.HEADING,
                file_path=file_path,
                line_start=i,
                line_end=i,
                metadata={"level": level}
            )
            headings.append(symbol)
        
        # Match Setext headings: Heading\n=====
        # Check if there's a next line (i is 1-indexed, but lines is 0-indexed)
        if i < len(lines):
            next_line = lines[i]  # lines[i] is the next line (0-indexed array)
            if re.match(r'^={3,}$', next_line):
                heading_text = line.strip()
                symbol = Symbol(
                    name=heading_text,
                    type=NodeType.HEADING,
                    file_path=file_path,
                    line_start=i,
                    line_end=i + 1,
                    metadata={"level": 1}
                )
                headings.append(symbol)
            elif re.match(r'^-{3,}$', next_line):
                heading_text = line.strip()
                symbol = Symbol(
                    name=heading_text,
                    type=NodeType.HEADING,
                    file_path=file_path,
                    line_start=i,
                    line_end=i + 1,
                    metadata={"level": 2}
                )
                headings.append(symbol)
    
    return headings


def _extract_todos(content: str) -> List[str]:
    """Extract TODO/FIXME from markdown."""
    todos = []
    
    # Match - [ ] TODO: ...
    pattern = r'- \[ \]\s*(TODO|FIXME):\s*(.+)'
    for match in re.finditer(pattern, content, re.IGNORECASE):
        todos.append(match.group(2).strip())
    
    # Match <!-- TODO: ... -->
    pattern = r'<!--\s*(TODO|FIXME):\s*(.+?)\s*-->'
    for match in re.finditer(pattern, content, re.IGNORECASE):
        todos.append(match.group(2).strip())
    
    return todos

