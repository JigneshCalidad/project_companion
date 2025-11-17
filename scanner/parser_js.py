"""JavaScript/TypeScript code parser using heuristics."""

import re
from typing import List, Optional
from scanner.schema import Symbol, NodeType, FileInfo


def parse_file(file_path: str) -> Optional[FileInfo]:
    """Parse a JavaScript/TypeScript file and extract symbols."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except UnicodeDecodeError:
        return None
    
    file_info = FileInfo(
        path=file_path,
        language="javascript" if file_path.endswith('.js') else "typescript",
        size=len(content),
        line_count=len(content.splitlines())
    )
    
    # Extract functions
    functions = _extract_functions(content, file_path)
    file_info.symbols.extend(functions)
    
    # Extract classes
    classes = _extract_classes(content, file_path)
    file_info.symbols.extend(classes)
    
    # Extract imports
    imports = _extract_imports(content)
    file_info.imports = imports
    
    # Extract TODOs
    todos = _extract_todos(content)
    file_info.todos = todos
    
    return file_info


def _extract_functions(content: str, file_path: str) -> List[Symbol]:
    """Extract function definitions using regex."""
    functions = []
    
    # Match function declarations: function name(...) { ... }
    pattern = r'function\s+(\w+)\s*\([^)]*\)\s*\{'
    for match in re.finditer(pattern, content):
        func_name = match.group(1)
        line_num = content[:match.start()].count('\n') + 1
        
        symbol = Symbol(
            name=func_name,
            type=NodeType.FUNCTION,
            file_path=file_path,
            line_start=line_num,
            line_end=line_num
        )
        functions.append(symbol)
    
    # Match arrow functions: const name = (...) => { ... }
    pattern = r'(?:const|let|var)\s+(\w+)\s*=\s*\([^)]*\)\s*=>'
    for match in re.finditer(pattern, content):
        func_name = match.group(1)
        line_num = content[:match.start()].count('\n') + 1
        
        symbol = Symbol(
            name=func_name,
            type=NodeType.FUNCTION,
            file_path=file_path,
            line_start=line_num,
            line_end=line_num,
            metadata={"arrow": True}
        )
        functions.append(symbol)
    
    # Match method definitions: name(...) { ... }
    pattern = r'(\w+)\s*\([^)]*\)\s*\{'
    for match in re.finditer(pattern, content):
        func_name = match.group(1)
        # Skip if it's already captured as a function or class
        if func_name not in [f.name for f in functions]:
            line_num = content[:match.start()].count('\n') + 1
            
            symbol = Symbol(
                name=func_name,
                type=NodeType.FUNCTION,
                file_path=file_path,
                line_start=line_num,
                line_end=line_num,
                metadata={"method": True}
            )
            functions.append(symbol)
    
    return functions


def _extract_classes(content: str, file_path: str) -> List[Symbol]:
    """Extract class definitions using regex."""
    classes = []
    
    # Match class declarations: class Name { ... }
    pattern = r'class\s+(\w+)(?:\s+extends\s+(\w+))?\s*\{'
    for match in re.finditer(pattern, content):
        class_name = match.group(1)
        extends = match.group(2)
        line_num = content[:match.start()].count('\n') + 1
        
        metadata = {}
        if extends:
            metadata["extends"] = extends
        
        symbol = Symbol(
            name=class_name,
            type=NodeType.CLASS,
            file_path=file_path,
            line_start=line_num,
            line_end=line_num,
            metadata=metadata
        )
        classes.append(symbol)
    
    return classes


def _extract_imports(content: str) -> List[str]:
    """Extract import statements."""
    imports = []
    
    # Match ES6 imports: import ... from 'module'
    pattern = r"import\s+(?:.*?\s+from\s+)?['\"]([^'\"]+)['\"]"
    for match in re.finditer(pattern, content):
        imports.append(match.group(1))
    
    # Match require statements: require('module')
    pattern = r"require\s*\(['\"]([^'\"]+)['\"]\)"
    for match in re.finditer(pattern, content):
        imports.append(match.group(1))
    
    return imports


def _extract_todos(content: str) -> List[str]:
    """Extract TODO/FIXME comments."""
    todos = []
    
    # Match single-line comments: // TODO: ...
    pattern = r'//\s*(TODO|FIXME|XXX|HACK):\s*(.+)'
    for match in re.finditer(pattern, content, re.IGNORECASE):
        todos.append(match.group(2).strip())
    
    # Match multi-line comments: /* TODO: ... */
    pattern = r'/\*\s*(TODO|FIXME|XXX|HACK):\s*(.+?)\*/'
    for match in re.finditer(pattern, content, re.IGNORECASE | re.DOTALL):
        todos.append(match.group(2).strip())
    
    return todos

