"""Tests for scanner module."""

import pytest
from pathlib import Path
from scanner.static_scanner import scan_repository
from scanner.parser_python import parse_file
from scanner.parser_js import parse_file as parse_js_file


def test_scan_sample_repo():
    """Test scanning the sample repository."""
    repo_path = Path(__file__).parent.parent / "examples" / "sample_repo"
    result = scan_repository(str(repo_path))
    
    assert result.root_path == str(repo_path.resolve())
    assert len(result.files) > 0
    assert len(result.graph_nodes) > 0
    assert len(result.graph_edges) > 0
    assert "total_files" in result.metadata


def test_parse_python_file():
    """Test parsing a Python file."""
    test_file = Path(__file__).parent.parent / "examples" / "sample_repo" / "module_a.py"
    file_info = parse_file(str(test_file))
    
    assert file_info is not None
    assert file_info.language == "python"
    assert len(file_info.symbols) > 0
    
    # Check for function
    function_names = [s.name for s in file_info.symbols if s.type.value == "function"]
    assert "calculate_sum" in function_names
    
    # Check for class
    class_names = [s.name for s in file_info.symbols if s.type.value == "class"]
    assert "Calculator" in class_names
    
    # Check for imports
    assert len(file_info.imports) > 0
    
    # Check for TODOs
    assert len(file_info.todos) > 0


def test_parse_js_file():
    """Test parsing a JavaScript file."""
    test_file = Path(__file__).parent.parent / "examples" / "sample_repo" / "module_b.js"
    file_info = parse_js_file(str(test_file))
    
    assert file_info is not None
    assert file_info.language in ("javascript", "typescript")
    assert len(file_info.symbols) > 0
    
    # Check for function
    function_names = [s.name for s in file_info.symbols if s.type.value == "function"]
    assert "formatDate" in function_names
    
    # Check for class
    class_names = [s.name for s in file_info.symbols if s.type.value == "class"]
    assert "UserManager" in class_names

