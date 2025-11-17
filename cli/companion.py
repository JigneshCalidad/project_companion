"""CLI interface for Project Companion."""

import click
import requests
import json
import sys
from pathlib import Path
from knowledge.store import KnowledgeStore
from scanner.static_scanner import scan_repository
from audit.audit_log import AuditLog


API_BASE_URL = "http://localhost:8000"


@click.group()
def main():
    """Project Companion CLI - Universal codebase understanding tool."""
    pass


@main.command()
@click.argument("path", type=click.Path(exists=True))
@click.option("--api", is_flag=True, help="Use API instead of local scanning")
def scan(path, api):
    """Scan a repository or directory."""
    click.echo(f"Scanning {path}...")
    
    if api:
        # Use API
        try:
            response = requests.post(
                f"{API_BASE_URL}/api/scan/static",
                json={"path": str(Path(path).resolve())}
            )
            response.raise_for_status()
            result = response.json()
            click.echo(f"✓ Scan completed: {result['nodes_added']} nodes, {result['edges_added']} edges")
            click.echo(f"  Scan ID: {result['scan_id']}")
        except requests.exceptions.ConnectionError:
            click.echo("Error: Could not connect to API. Is the server running?", err=True)
            sys.exit(1)
        except Exception as e:
            click.echo(f"Error: {e}", err=True)
            sys.exit(1)
    else:
        # Local scan
        try:
            scan_result = scan_repository(path)
            knowledge_store = KnowledgeStore()
            scan_id = knowledge_store.add_scan(scan_result)
            click.echo(f"✓ Scan completed: {len(scan_result.graph_nodes)} nodes, {len(scan_result.graph_edges)} edges")
            click.echo(f"  Scan ID: {scan_id}")
        except Exception as e:
            click.echo(f"Error: {e}", err=True)
            sys.exit(1)


@main.command()
@click.argument("question")
@click.option("--api", is_flag=True, help="Use API instead of local query")
def ask(question, api):
    """Ask a question about the codebase."""
    if api:
        try:
            response = requests.post(
                f"{API_BASE_URL}/api/ask",
                json={"question": question}
            )
            response.raise_for_status()
            result = response.json()
            
            click.echo(f"\nQuestion: {result['question']}")
            click.echo(f"Found {result['total_matches']} matches\n")
            
            if result['matches']:
                click.echo("Matches:")
                for match in result['matches'][:10]:
                    click.echo(f"  • {match.get('label', 'Unknown')} ({match.get('type', 'unknown')})")
            
            if result['related']:
                click.echo("\nRelated:")
                for rel in result['related'][:5]:
                    click.echo(f"  • {rel.get('label', 'Unknown')}")
        except requests.exceptions.ConnectionError:
            click.echo("Error: Could not connect to API. Is the server running?", err=True)
            sys.exit(1)
        except Exception as e:
            click.echo(f"Error: {e}", err=True)
            sys.exit(1)
    else:
        knowledge_store = KnowledgeStore()
        result = knowledge_store.query(question)
        
        click.echo(f"\nQuestion: {result['question']}")
        click.echo(f"Found {result['total_matches']} matches\n")
        
        if result['matches']:
            click.echo("Matches:")
            for match in result['matches'][:10]:
                click.echo(f"  • {match.get('label', 'Unknown')} ({match.get('type', 'unknown')})")


@main.group()
def export():
    """Export knowledge graph data."""
    pass


@export.command("graph")
@click.option("--format", type=click.Choice(["json", "mermaid"]), default="json")
@click.option("--output", type=click.Path(), help="Output file path")
def export_graph(format, output):
    """Export the knowledge graph."""
    knowledge_store = KnowledgeStore()
    
    if format == "json":
        data = knowledge_store.export_json()
        output_text = json.dumps(data, indent=2)
    else:  # mermaid
        output_text = knowledge_store.export_mermaid()
    
    if output:
        Path(output).write_text(output_text)
        click.echo(f"✓ Exported to {output}")
    else:
        click.echo(output_text)


@main.group()
def action():
    """Action management commands."""
    pass


@action.command("request")
@click.option("--cmd", required=True, help="Command to execute")
@click.option("--type", default="command", help="Action type")
def request_action(cmd, type):
    """Request an action to be performed."""
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/actions/request",
            json={
                "action_type": type,
                "command": cmd,
                "details": {}
            }
        )
        response.raise_for_status()
        result = response.json()
        click.echo(f"✓ Action requested: ID {result['action_id']}")
        click.echo(f"  Status: {result['status']}")
        click.echo(f"  Message: {result['message']}")
    except requests.exceptions.ConnectionError:
        click.echo("Error: Could not connect to API. Is the server running?", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@action.command("list")
def list_actions():
    """List pending actions."""
    try:
        response = requests.get(f"{API_BASE_URL}/api/actions/pending")
        response.raise_for_status()
        actions = response.json()
        
        if not actions:
            click.echo("No pending actions.")
            return
        
        click.echo("Pending actions:")
        for action in actions:
            click.echo(f"  ID: {action['id']}")
            click.echo(f"  Type: {action['action_type']}")
            click.echo(f"  User: {action['user']}")
            click.echo(f"  Details: {action['details']}")
            click.echo()
    except requests.exceptions.ConnectionError:
        click.echo("Error: Could not connect to API. Is the server running?", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@action.command("approve")
@click.argument("action_id", type=int)
@click.option("--reject", is_flag=True, help="Reject instead of approve")
def approve_action(action_id, reject):
    """Approve an action."""
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/actions/approve",
            json={
                "action_id": action_id,
                "approved": not reject,
                "user": "cli_user"
            }
        )
        response.raise_for_status()
        result = response.json()
        click.echo(f"✓ Action {action_id}: {result['status']}")
        click.echo(f"  Message: {result['message']}")
    except requests.exceptions.ConnectionError:
        click.echo("Error: Could not connect to API. Is the server running?", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@main.command()
def stats():
    """Show knowledge graph statistics."""
    knowledge_store = KnowledgeStore()
    stats = knowledge_store.get_statistics()
    
    click.echo("Knowledge Graph Statistics:")
    click.echo(f"  Nodes: {stats['node_count']}")
    click.echo(f"  Edges: {stats['edge_count']}")
    click.echo(f"  Connected: {stats['is_connected']}")
    click.echo(f"  Components: {stats['components']}")


if __name__ == "__main__":
    main()

