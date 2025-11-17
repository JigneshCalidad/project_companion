"""Python code parser using AST."""

import ast
import io
import tokenize
from typing import List, Optional

from scanner.schema import Symbol, NodeType, FileInfo


def parse_file(file_path: str) -> Optional[FileInfo]:
    """Parse a Python file and extract symbols."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
            tree = ast.parse(content, filename=file_path)
    except (SyntaxError, UnicodeDecodeError) as e:
        # Skip files that can't be parsed
        return None
    
    file_info = FileInfo(
        path=file_path,
        language="python",
        size=len(content),
        line_count=len(content.splitlines())
    )
    
    visitor = PythonVisitor(file_path)
    visitor.visit(tree)
    
    file_info.symbols = visitor.symbols
    file_info.imports = visitor.imports
    comment_todos = _extract_comment_todos(content)
    file_info.todos = visitor.todos + comment_todos
    
    return file_info


def _extract_comment_todos(content: str) -> List[str]:
    """Capture TODO/FIXME style comments using tokenize for accuracy."""
    todos: List[str] = []
    reader = io.StringIO(content).readline
    try:
        for token in tokenize.generate_tokens(reader):
            if token.type == tokenize.COMMENT:
                comment_text = token.string.lstrip("#").strip()
                lowered = comment_text.lower()
                if "todo" in lowered or "fixme" in lowered:
                    todos.append(comment_text or token.string)
    except tokenize.TokenError:
        # Malformed files aren't critical for TODO extraction
        pass
    return todos


class PythonVisitor(ast.NodeVisitor):
    """AST visitor to extract symbols from Python code."""
    
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.symbols: List[Symbol] = []
        self.imports: List[str] = []
        self.todos: List[str] = []
    
    def visit_FunctionDef(self, node):
        """Extract function definitions."""
        docstring = ast.get_docstring(node)
        signature = self._get_function_signature(node)
        
        symbol = Symbol(
            name=node.name,
            type=NodeType.FUNCTION,
            file_path=self.file_path,
            line_start=node.lineno,
            line_end=node.end_lineno or node.lineno,
            docstring=docstring,
            signature=signature
        )
        self.symbols.append(symbol)
        self.generic_visit(node)
    
    def visit_AsyncFunctionDef(self, node):
        """Extract async function definitions."""
        docstring = ast.get_docstring(node)
        signature = self._get_function_signature(node)
        
        symbol = Symbol(
            name=node.name,
            type=NodeType.FUNCTION,
            file_path=self.file_path,
            line_start=node.lineno,
            line_end=node.end_lineno or node.lineno,
            docstring=docstring,
            signature=signature,
            metadata={"async": True}
        )
        self.symbols.append(symbol)
        self.generic_visit(node)
    
    def visit_ClassDef(self, node):
        """Extract class definitions."""
        docstring = ast.get_docstring(node)
        bases = []
        if hasattr(ast, 'unparse'):
            bases = [ast.unparse(base) for base in node.bases]
        else:
            # Fallback for older Python versions
            for base in node.bases:
                if isinstance(base, ast.Name):
                    bases.append(base.id)
        
        symbol = Symbol(
            name=node.name,
            type=NodeType.CLASS,
            file_path=self.file_path,
            line_start=node.lineno,
            line_end=node.end_lineno or node.lineno,
            docstring=docstring,
            metadata={"bases": bases}
        )
        self.symbols.append(symbol)
        self.generic_visit(node)
    
    def visit_Import(self, node):
        """Extract import statements."""
        for alias in node.names:
            self.imports.append(alias.name)
        self.generic_visit(node)
    
    def visit_ImportFrom(self, node):
        """Extract from-import statements."""
        module = node.module or ""
        for alias in node.names:
            import_name = f"{module}.{alias.name}" if module else alias.name
            self.imports.append(import_name)
        self.generic_visit(node)
    
    def visit_Assign(self, node):
        """Extract variable assignments (module-level only)."""
        # Only track module-level variables
        if isinstance(node.targets[0], ast.Name):
            var_name = node.targets[0].id
            symbol = Symbol(
                name=var_name,
                type=NodeType.VARIABLE,
                file_path=self.file_path,
                line_start=node.lineno,
                line_end=node.lineno
            )
            self.symbols.append(symbol)
        self.generic_visit(node)
    
    def _get_function_signature(self, node) -> str:
        """Generate function signature string."""
        try:
            if hasattr(ast, 'unparse'):
                return ast.unparse(node)
            # Fallback for older Python versions
            args = [arg.arg for arg in node.args.args]
            return f"def {node.name}({', '.join(args)})"
        except Exception:
            return f"def {node.name}(...)"
    
    def generic_visit(self, node):
        """Override to extract TODO comments."""
        if isinstance(node, ast.Expr) and isinstance(node.value, ast.Constant):
            if isinstance(node.value.value, str):
                content = node.value.value.lower()
                if 'todo' in content or 'fixme' in content:
                    self.todos.append(node.value.value)
        
        super().generic_visit(node)

