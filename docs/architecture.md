# Architecture Documentation

## System Overview

Project Companion is built on a modular architecture that separates concerns into distinct layers:

```
┌─────────────────────────────────────────┐
│           User Interface                │
│  (React UI / CLI / API Consumers)      │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│         FastAPI Backend                 │
│  (Routes, Services, Dependencies)      │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│      Business Logic Layer               │
│  (ScanService, GraphService, etc.)      │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│      Data Access Layer                  │
│  (KnowledgeStore, AuditLog)             │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│      Scanner Layer                      │
│  (StaticScanner, Parsers, Indexers)     │
└─────────────────────────────────────────┘
```

## Core Components

### Scanner Module

**Purpose**: Extract information from codebases

**Components**:
- `static_scanner.py`: Orchestrates scanning process
- `file_indexer.py`: Walks directories and identifies files
- `parser_*.py`: Language-specific parsers (Python, JavaScript, Markdown)
- `dynamic_scanner.py`: Playwright-based web scanning

**Design Decisions**:
- Language-specific parsers for accuracy
- Heuristic fallback for unsupported languages
- Extensible parser interface

### Knowledge Graph

**Purpose**: Store and query codebase relationships

**Components**:
- `KnowledgeStore`: Manages graph persistence
- NetworkX for in-memory graph operations
- SQLite for persistent storage

**Graph Structure**:
- **Nodes**: Files, functions, classes, variables, TODOs
- **Edges**: Imports, calls, contains, references

### API Layer

**Purpose**: Expose functionality via REST API

**Routes**:
- `/api/scan/*`: Scanning operations
- `/api/ask`: Query the knowledge graph
- `/api/actions/*`: Action request/approval workflow
- `/api/graph/*`: Graph export and statistics
- `/api/settings`: Configuration management

### Security Layer

**Purpose**: Enforce security boundaries

**Components**:
- `PermissionService`: Manages permissions
- `AuditLog`: Tracks all actions
- Action approval workflow

**Principles**:
- Read-only by default
- Explicit approval required
- All actions logged
- Ephemeral credentials

## Data Flow

### Scanning Flow

```
Repository → FileIndexer → Parsers → ScanResult → KnowledgeStore → Graph
```

1. `scan_repository()` walks the directory tree
2. Files are identified and categorized by language
3. Language-specific parsers extract symbols
4. Graph nodes and edges are built
5. Results are stored in the knowledge graph

### Query Flow

```
Question → GraphService → KnowledgeStore → Graph Traversal → Results
```

1. User asks a question
2. Keywords are extracted
3. Graph is traversed to find matches
4. Related nodes are discovered
5. Results are formatted and returned

### Action Flow

```
Request → AuditLog → Approval → Execute → AuditLog
```

1. Action is requested
2. Request is logged
3. User approves/rejects
4. If approved, action executes
5. Result is logged

## Storage Schema

### SQLite Tables

**nodes**:
- `id` (TEXT PRIMARY KEY)
- `type` (TEXT)
- `label` (TEXT)
- `data` (TEXT JSON)
- `created_at`, `updated_at` (TIMESTAMP)

**edges**:
- `id` (INTEGER PRIMARY KEY)
- `source` (TEXT, FK to nodes)
- `target` (TEXT, FK to nodes)
- `type` (TEXT)
- `data` (TEXT JSON)
- `created_at` (TIMESTAMP)

**scans**:
- `id` (INTEGER PRIMARY KEY)
- `root_path` (TEXT)
- `metadata` (TEXT JSON)
- `created_at` (TIMESTAMP)

**audit_log**:
- `id` (INTEGER PRIMARY KEY)
- `timestamp` (TIMESTAMP)
- `action_type` (TEXT)
- `user` (TEXT)
- `details` (TEXT JSON)
- `status` (TEXT)
- `approved_by` (TEXT)
- `approved_at` (TIMESTAMP)
- `result` (TEXT JSON)

## Extension Points

### Adding a New Parser

1. Create `scanner/parser_<language>.py`
2. Implement `parse_file(file_path: str) -> Optional[FileInfo]`
3. Register in `static_scanner.py`

### Adding a New Route

1. Create route file in `app/routes/`
2. Define Pydantic models for request/response
3. Implement service logic
4. Register router in `app/main.py`

### Adding a New Query Type

1. Extend `KnowledgeStore.query()`
2. Add graph traversal logic
3. Format results appropriately

## Performance Considerations

- **Large Repositories**: Scanning is O(n) where n is number of files
- **Graph Queries**: NetworkX provides efficient graph operations
- **Database**: SQLite is suitable for single-user scenarios
- **Caching**: Consider adding Redis for multi-user deployments

## Security Considerations

- All file operations are read-only by default
- Dynamic scanning requires explicit enablement
- Actions require approval workflow
- Audit log is append-only
- Secrets are never stored in plaintext

## Future Enhancements

- Embedding-based semantic search
- Real-time graph updates
- Multi-repository support
- Collaborative features
- IDE integrations
- CI/CD pipeline integration

