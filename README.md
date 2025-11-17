# Project Companion

> A universal project companion bot that deeply understands your codebase through knowledge graphs and conversational intelligence.

## 🌱 Conceptual Overview

**Why Project Companion Exists**

Modern software projects are complex ecosystems. Understanding them requires navigating thousands of files, dependencies, patterns, and relationships. Project Companion bridges this gap by building a **living knowledge graph** of your entire codebase—every file, function, class, import, and relationship—then making that knowledge accessible through natural conversation.

**The Core Pattern**

1. **Scan** → Walk the entire repository, parsing code, comments, and structure
2. **Graph** → Build a knowledge graph connecting files, symbols, and concepts
3. **Remember** → Store this knowledge persistently in a local database
4. **Answer** → Query the graph to answer questions about your project
5. **Act** → Request actions (with explicit approval) to perform tasks safely

**The Philosophy**

This tool respects boundaries. It's **read-only by default**. Any action that could modify your project requires explicit human approval. Security isn't an afterthought—it's the foundation.

---

## 🏗️ How It Works

### Architecture Flow

```
Repository → Scanner → Knowledge Graph → Query Engine → Conversation
                ↓
          Audit Log (all actions)
```

**Static Scanning**: Parses code files, extracts symbols, builds relationships  
**Knowledge Graph**: NetworkX graph stored in SQLite with embeddings  
**Conversational Interface**: Query the graph using natural language  
**Action System**: Request → Approve → Execute workflow for safe automation

### Key Components

- **Scanner**: Universal code parser (Python AST, JS heuristics, Markdown, YAML)
- **Knowledge Store**: SQLite + NetworkX for persistent graph storage
- **API**: FastAPI backend exposing scan, ask, and action endpoints
- **CLI**: Command-line interface for quick interactions
- **UI**: React frontend for visual exploration and conversation

---

## 🚀 Quickstart

### Prerequisites

- Python 3.11+
- Node.js 18+ (for UI)
- Git

### Installation

```bash
# Clone the repository
git clone git@github.com:JigneshCalidad/project_companion.git
cd project_companion

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -e ".[dev]"

# Install Playwright (optional, for dynamic scanning)
playwright install chromium

# Install UI dependencies
cd ui
npm install
cd ..
```

### Running the Server

```bash
# Start the FastAPI backend
uvicorn app.main:app --reload --port 8000
```

The API will be available at `http://localhost:8000`  
API docs at `http://localhost:8000/docs`

### Running the CLI

```bash
# Scan a repository
companion scan /path/to/repo

# Ask a question
companion ask "What does the main function do?"

# Export the knowledge graph
companion export graph --format json

# Request an action (requires approval)
companion request-action --cmd "git mv old.py new.py"
```

### Running the UI

```bash
cd ui
npm run dev
```

Open `http://localhost:5173` in your browser.

---

## 💬 Example Questions

Once you've scanned a repository, try asking:

- "What are the main entry points of this application?"
- "Show me all functions that use the database connection"
- "What dependencies does module X have?"
- "Where are error handlers defined?"
- "What TODOs are mentioned in the codebase?"
- "How is authentication implemented?"

---

## 🔍 Example Scans

### Scan a Local Repository

```bash
companion scan /Users/apple/projects/my-app
```

### Scan the Example Repository

```bash
companion scan examples/sample_repo
```

The scanner will:
- Walk all files and directories
- Parse code files (Python, JavaScript, etc.)
- Extract symbols (functions, classes, variables)
- Build import/reference relationships
- Store everything in the knowledge graph

---

## 🛡️ Security & Boundaries

**Default Behavior**: Read-only. The bot never modifies your code without explicit approval.

**Action Workflow**:
1. Request an action via CLI or API
2. Action is logged in audit log
3. User must approve via UI or CLI
4. Action executes with ephemeral credentials
5. Result is logged

**Secrets Management**:
- Never store secrets in plaintext
- Use environment variables or encrypted keystores
- See `SECURITY.md` for detailed practices

**Dynamic Scanning**:
- Playwright-based web scanning is **disabled by default**
- Must be explicitly enabled in settings
- Requires user confirmation before each scan

See `SECURITY.md` for comprehensive security guidelines.

---

## ⚙️ Advanced Features

### Enabling Dynamic Scanning

1. Set `ENABLE_DYNAMIC_SCAN=true` in `.env`
2. Configure target URL in settings
3. Confirm in UI before scanning

### GitHub Integration

1. Create a GitHub App or OAuth token
2. Store credentials securely (see `docs/oauth_example.md`)
3. Use `companion scan github://owner/repo` with token

### Vault Integration

For production deployments, integrate HashiCorp Vault:
- See `docs/vault_integration.md`
- Store tokens and secrets in Vault
- Use ephemeral credentials only

---

## 📚 Learning Path

This project is designed for deep understanding. See `EXERCISES.md` for hands-on labs:

- **Lab 1**: Run the scanner and explore the knowledge graph
- **Lab 2**: Ask questions about the sample repository
- **Lab 3**: Request and approve a safe action
- **Lab 4**: Enable dynamic scanning manually
- **Lab 5**: Connect a GitHub repository using OAuth

---

## 🧠 Reflection Prompts

After working with Project Companion, consider:

- How does the knowledge graph representation differ from your mental model of the codebase?
- What relationships did you discover that you weren't aware of?
- How might this tool change your approach to onboarding new team members?
- What boundaries feel most important when automating codebase actions?

---

## 📖 Documentation

- `docs/architecture.md` - System architecture and design decisions
- `docs/oauth_example.md` - GitHub OAuth integration guide
- `docs/vault_integration.md` - HashiCorp Vault setup
- `docs/conventions.md` - Code style and contribution guidelines
- `SECURITY.md` - Security practices and threat model
- `EXERCISES.md` - Hands-on learning labs

---

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov=scanner --cov=knowledge

# Run specific test file
pytest tests/test_scanner.py
```

---

## 🚧 Limitations

- **Language Support**: Currently optimized for Python and JavaScript. Other languages use heuristic parsing.
- **Large Repositories**: Very large repos (>100k files) may take significant time to scan.
- **Dynamic Analysis**: Limited to static analysis by default. Dynamic scanning requires explicit enablement.
- **Real-time Updates**: The knowledge graph doesn't auto-update. Re-scan after significant changes.

---

## 🤝 Contributing

See `docs/conventions.md` for contribution guidelines.

---

## 📄 License

MIT License - See LICENSE file for details.

---

## 🌟 How This Connects to Your Broader Goals

Project Companion embodies the principle that **understanding precedes action**. By building a comprehensive knowledge graph, you're not just creating a tool—you're creating a **reflective mirror** of your codebase that reveals patterns, dependencies, and relationships that might otherwise remain hidden.

This tool supports:
- **Onboarding**: New team members can ask questions instead of reading thousands of files
- **Refactoring**: Understand impact before making changes
- **Documentation**: Generate insights from code structure itself
- **Security**: Audit all actions, require explicit approval

The knowledge graph becomes a **living artifact** that grows with your project, serving as both a map and a memory of your codebase's evolution.

