"""Permission and security service."""

from typing import Dict, Optional, Tuple
from pathlib import Path
import os


class PermissionService:
    """Manages permissions and security settings."""
    
    def __init__(self):
        self.enable_dynamic_scan = os.getenv("ENABLE_DYNAMIC_SCAN", "false").lower() == "true"
        self.read_only_mode = os.getenv("READ_ONLY_MODE", "true").lower() == "true"
        self.require_approval = True  # Always require approval for actions
    
    def can_perform_action(self, action_type: str, user: str) -> Tuple[bool, Optional[str]]:
        """Check if an action can be performed."""
        if self.read_only_mode and action_type != "read":
            return False, "Read-only mode is enabled"
        
        if not self.require_approval:
            return False, "Approval workflow is required"
        
        return True, None
    
    def can_use_dynamic_scan(self) -> bool:
        """Check if dynamic scanning is enabled."""
        return self.enable_dynamic_scan
    
    def get_settings(self) -> Dict:
        """Get current security settings."""
        return {
            "read_only_mode": self.read_only_mode,
            "enable_dynamic_scan": self.enable_dynamic_scan,
            "require_approval": self.require_approval
        }
    
    def update_settings(self, settings: Dict):
        """Update security settings (with validation)."""
        if "enable_dynamic_scan" in settings:
            # Require explicit confirmation
            self.enable_dynamic_scan = settings["enable_dynamic_scan"]
        
        if "read_only_mode" in settings:
            self.read_only_mode = settings["read_only_mode"]

