# Hands-On Labs

These exercises guide you through Project Companion's features, building understanding through practice.

---

## Lab 1: Run the Scanner and View the Knowledge Graph

**Goal**: Understand how Project Companion builds its knowledge representation.

**Steps**:

1. **Start the backend server**:
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```

2. **Scan the example repository**:
   ```bash
   companion scan examples/sample_repo
   ```

3. **Explore the knowledge graph via API**:
   ```bash
   curl http://localhost:8000/api/graph/nodes | jq
   ```

4. **Export the graph**:
   ```bash
   companion export graph --format json > graph.json
   companion export graph --format mermaid > graph.mmd
   ```

5. **Visualize the Mermaid diagram**:
   - Copy `graph.mmd` content
   - Paste into [Mermaid Live Editor](https://mermaid.live)
   - Observe the relationships between files and symbols

**Reflection Questions**:
- What types of relationships did the scanner discover?
- How does the graph structure reflect the codebase organization?
- What information might be missing from the graph?

---

## Lab 2: Ask Questions About the Sample Repository

**Goal**: Experience the conversational interface and understand how queries map to graph traversal.

**Steps**:

1. **Ensure the server is running** (from Lab 1)

2. **Ask questions via CLI**:
   ```bash
   companion ask "What functions are defined in module_a.py?"
   companion ask "What are the main entry points of this project?"
   companion ask "Show me all TODOs mentioned in the codebase"
   ```

3. **Ask questions via API**:
   ```bash
   curl -X POST http://localhost:8000/api/ask \
     -H "Content-Type: application/json" \
     -d '{"question": "What does the calculate function do?"}'
   ```

4. **Try the UI**:
   - Start the UI: `cd ui && npm run dev`
   - Open `http://localhost:5173`
   - Use the chat interface to ask questions

**Experimentation**:
- Try questions that require traversing multiple relationships
- Ask about concepts that span multiple files
- Compare answers to what you know about the codebase

**Reflection Questions**:
- How does the bot's understanding compare to your own?
- What types of questions work best?
- What limitations do you notice?

---

## Lab 3: Request a Safe Action → Approve → Apply

**Goal**: Understand the action request and approval workflow.

**Steps**:

1. **Request an action**:
   ```bash
   companion request-action --cmd "ls -la examples/sample_repo"
   ```
   Note the action ID returned.

2. **View pending actions**:
   ```bash
   curl http://localhost:8000/api/actions/pending | jq
   ```

3. **Review the audit log**:
   ```bash
   tail -f audit/audit.log
   ```

4. **Approve the action**:
   ```bash
   companion approve <action_id>
   ```

5. **Verify execution**:
   - Check the audit log for execution result
   - Verify the command output

**Safety Practice**:
- Try requesting a potentially dangerous action (it will still require approval)
- Observe how the system prevents automatic execution
- Review the audit trail

**Reflection Questions**:
- How does the approval workflow make you feel about automation?
- What types of actions would you trust with this system?
- How might you extend the approval workflow?

---

## Lab 4: Enable Dynamic Scanning Manually

**Goal**: Understand how dynamic scanning works and why it requires explicit enablement.

**Prerequisites**:
- Playwright installed: `playwright install chromium`
- A simple web app to scan (or use the example)

**Steps**:

1. **Check current settings**:
   ```bash
   curl http://localhost:8000/api/settings | jq
   ```

2. **Enable dynamic scanning** (via API or UI):
   ```bash
   curl -X POST http://localhost:8000/api/settings \
     -H "Content-Type: application/json" \
     -d '{"enable_dynamic_scan": true}'
   ```

3. **Confirm in UI**:
   - Open the Settings page
   - Review the warning about dynamic scanning
   - Confirm your consent

4. **Run a dynamic scan**:
   ```bash
   companion scan --dynamic http://localhost:3000
   ```

5. **Review results**:
   - Check what pages were discovered
   - Review DOM structure captured
   - Observe network requests logged

**Security Reflection**:
- Why is dynamic scanning disabled by default?
- What risks does it introduce?
- How does explicit consent mitigate those risks?

---

## Lab 5: Connect a GitHub Repository Using OAuth

**Goal**: Learn secure credential management and repository access.

**Prerequisites**:
- GitHub account
- Personal Access Token (PAT) or GitHub App

**Steps**:

1. **Create a GitHub Personal Access Token**:
   - Go to GitHub Settings → Developer settings → Personal access tokens
   - Create token with `repo` scope (read-only)
   - Copy the token

2. **Store the token securely**:
   ```bash
   # Add to .env file (never commit this)
   echo "GITHUB_TOKEN=ghp_your_token_here" >> .env
   ```

3. **Scan a GitHub repository**:
   ```bash
   companion scan github://owner/repo-name
   ```

4. **Verify access**:
   - Check that the scan completes successfully
   - Review the knowledge graph for the remote repository
   - Confirm no credentials are logged

5. **Review security**:
   - Check `.gitignore` includes `.env`
   - Verify token is not in any committed files
   - Review `SECURITY.md` for best practices

**Advanced**:
- Set up a GitHub App instead of PAT
- Use HashiCorp Vault for credential storage
- Implement token rotation

**Reflection Questions**:
- How does token management differ from local scanning?
- What additional security considerations apply?
- How might you automate credential rotation?

---

## Lab 6: Extend the Scanner (Optional)

**Goal**: Understand the scanner architecture and add support for a new language.

**Steps**:

1. **Study the existing parsers**:
   - Review `scanner/parser_python.py`
   - Review `scanner/parser_js.py`
   - Understand the parser interface

2. **Create a new parser**:
   - Create `scanner/parser_rust.py` (or another language)
   - Implement the `parse_file()` function
   - Extract symbols and relationships

3. **Register the parser**:
   - Update `scanner/static_scanner.py` to use your parser
   - Add tests for the new parser

4. **Test your parser**:
   ```bash
   companion scan /path/to/rust/project
   ```

**Reflection Questions**:
- What patterns did you notice across parsers?
- How does the parser interface support extensibility?
- What challenges did you encounter?

---

## Lab 7: Build a Custom Query (Optional)

**Goal**: Understand the knowledge graph query system and create custom queries.

**Steps**:

1. **Explore the graph structure**:
   ```bash
   companion export graph --format json | jq '.nodes[] | select(.type=="function")'
   ```

2. **Write a custom query function**:
   - Create `knowledge/custom_queries.py`
   - Implement a function that queries the graph
   - Add it to the API

3. **Test your query**:
   ```bash
   curl -X POST http://localhost:8000/api/custom-query \
     -H "Content-Type: application/json" \
     -d '{"query_type": "your_custom_query", "params": {...}}'
   ```

**Reflection Questions**:
- What insights can custom queries reveal?
- How might you optimize graph traversal?
- What queries would be most valuable for your use case?

---

## Completion Checklist

- [ ] Completed Lab 1: Scanner and knowledge graph
- [ ] Completed Lab 2: Conversational interface
- [ ] Completed Lab 3: Action approval workflow
- [ ] Completed Lab 4: Dynamic scanning
- [ ] Completed Lab 5: GitHub integration
- [ ] (Optional) Lab 6: Extend scanner
- [ ] (Optional) Lab 7: Custom queries

---

## Next Steps

After completing these labs, consider:

1. **Scan your own projects**: Apply Project Companion to real repositories
2. **Customize the UI**: Add features specific to your workflow
3. **Extend the scanner**: Add support for your preferred languages
4. **Build integrations**: Connect to your CI/CD pipeline or IDE
5. **Contribute**: Share improvements with the community

---

**Remember**: These labs are designed for exploration and understanding. Take time to reflect on each exercise and consider how the concepts apply to your own work.

