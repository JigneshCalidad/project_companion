"""Audit logging for all actions."""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional, List
import sqlite3


class AuditLog:
    """Append-only audit log for tracking all actions."""
    
    def __init__(self, log_path: str = "audit/audit.log", db_path: str = "audit/audit.db"):
        """Initialize audit logging."""
        self.log_path = Path(log_path)
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_database()
    
    def _init_database(self):
        """Initialize SQLite database for structured audit logs."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS audit_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    action_type TEXT NOT NULL,
                    user TEXT,
                    details TEXT,
                    status TEXT,
                    approved_by TEXT,
                    approved_at TIMESTAMP,
                    result TEXT
                )
            """)
            
            conn.commit()
    
    def log_action_request(self, action_type: str, user: str, details: Dict) -> int:
        """Log an action request."""
        timestamp = datetime.now()
        details_json = json.dumps(details)
        
        # Write to text log
        log_entry = f"[{timestamp.isoformat()}] ACTION_REQUEST: user={user}, type={action_type}, details={details_json}, status=pending\n"
        with open(self.log_path, 'a') as f:
            f.write(log_entry)
        
        # Write to database
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO audit_log (timestamp, action_type, user, details, status)
                VALUES (?, ?, ?, ?, ?)
            """, (timestamp, action_type, user, details_json, "pending"))
            action_id = cursor.lastrowid
            conn.commit()
        
        return action_id
    
    def log_action_approval(self, action_id: int, approved_by: str, approved: bool):
        """Log action approval."""
        timestamp = datetime.now()
        
        log_entry = f"[{timestamp.isoformat()}] ACTION_APPROVE: action_id={action_id}, approved_by={approved_by}, approved={approved}\n"
        with open(self.log_path, 'a') as f:
            f.write(log_entry)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE audit_log
                SET approved_by = ?, approved_at = ?, status = ?
                WHERE id = ?
            """, (approved_by, timestamp, "approved" if approved else "rejected", action_id))
            conn.commit()
    
    def log_action_execution(self, action_id: int, result: Dict, success: bool):
        """Log action execution result."""
        timestamp = datetime.now()
        result_json = json.dumps(result)
        status = "success" if success else "failed"
        
        log_entry = f"[{timestamp.isoformat()}] ACTION_EXECUTE: action_id={action_id}, status={status}, result={result_json}\n"
        with open(self.log_path, 'a') as f:
            f.write(log_entry)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE audit_log
                SET status = ?, result = ?
                WHERE id = ?
            """, (status, result_json, action_id))
            conn.commit()
    
    def get_pending_actions(self) -> List[Dict]:
        """Get all pending actions."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, timestamp, action_type, user, details, status
                FROM audit_log
                WHERE status = 'pending'
                ORDER BY timestamp DESC
            """)
            
            actions = []
            for row in cursor.fetchall():
                actions.append({
                    "id": row[0],
                    "timestamp": row[1],
                    "action_type": row[2],
                    "user": row[3],
                    "details": json.loads(row[4]),
                    "status": row[5]
                })
        
        return actions
    
    def get_action(self, action_id: int) -> Optional[Dict]:
        """Get a specific action by ID."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, timestamp, action_type, user, details, status, approved_by, approved_at, result
                FROM audit_log
                WHERE id = ?
            """, (action_id,))
            
            row = cursor.fetchone()
        
        if not row:
            return None
        
        return {
            "id": row[0],
            "timestamp": row[1],
            "action_type": row[2],
            "user": row[3],
            "details": json.loads(row[4]) if row[4] else {},
            "status": row[5],
            "approved_by": row[6],
            "approved_at": row[7],
            "result": json.loads(row[8]) if row[8] else None
        }

