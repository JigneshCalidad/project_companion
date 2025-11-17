"""Action request and approval routes."""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
from app.services.permissions import PermissionService
from audit.audit_log import AuditLog


router = APIRouter(prefix="/api/actions", tags=["actions"])


class ActionRequest(BaseModel):
    action_type: str
    command: Optional[str] = None
    details: dict = {}


class ActionResponse(BaseModel):
    action_id: int
    status: str
    message: str


class ApprovalRequest(BaseModel):
    action_id: int
    approved: bool
    user: str = "default_user"  # In production, get from auth


def get_audit_log() -> AuditLog:
    """Dependency to get audit log."""
    return AuditLog()


def get_permission_service() -> PermissionService:
    """Dependency to get permission service."""
    return PermissionService()


@router.post("/request", response_model=ActionResponse)
async def request_action(
    request: ActionRequest,
    audit_log: AuditLog = Depends(get_audit_log),
    permission_service: PermissionService = Depends(get_permission_service)
):
    """Request an action to be performed."""
    can_perform, reason = permission_service.can_perform_action(
        request.action_type, "default_user"
    )
    
    if not can_perform:
        raise HTTPException(status_code=403, detail=reason or "Action not permitted")
    
    details = {
        "command": request.command,
        **request.details
    }
    
    action_id = audit_log.log_action_request(
        request.action_type,
        "default_user",
        details
    )
    
    return ActionResponse(
        action_id=action_id,
        status="pending",
        message="Action requested and pending approval"
    )


@router.get("/pending")
async def get_pending_actions(audit_log: AuditLog = Depends(get_audit_log)):
    """Get all pending actions."""
    return audit_log.get_pending_actions()


@router.get("/{action_id}")
async def get_action(
    action_id: int,
    audit_log: AuditLog = Depends(get_audit_log)
):
    """Get a specific action by ID."""
    action = audit_log.get_action(action_id)
    if not action:
        raise HTTPException(status_code=404, detail="Action not found")
    return action


@router.post("/approve", response_model=ActionResponse)
async def approve_action(
    request: ApprovalRequest,
    audit_log: AuditLog = Depends(get_audit_log)
):
    """Approve or reject an action."""
    action = audit_log.get_action(request.action_id)
    if not action:
        raise HTTPException(status_code=404, detail="Action not found")
    
    if action["status"] != "pending":
        raise HTTPException(status_code=400, detail=f"Action is already {action['status']}")
    
    audit_log.log_action_approval(request.action_id, request.user, request.approved)
    
    if request.approved:
        # Execute the action (simplified - in production, use a task queue)
        try:
            import subprocess
            import shlex
            if action["details"].get("command"):
                # Security: Use shell=False and split command to prevent injection
                command_str = action["details"]["command"]
                # Split command safely - only allow simple commands
                # In production, use a whitelist of allowed commands
                command_parts = shlex.split(command_str)
                if not command_parts:
                    raise ValueError("Empty command")
                
                result = subprocess.run(
                    command_parts,
                    shell=False,
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                audit_log.log_action_execution(
                    request.action_id,
                    {
                        "stdout": result.stdout,
                        "stderr": result.stderr,
                        "returncode": result.returncode
                    },
                    result.returncode == 0
                )
        except Exception as e:
            audit_log.log_action_execution(
                request.action_id,
                {"error": str(e)},
                False
            )
    
    return ActionResponse(
        action_id=request.action_id,
        status="approved" if request.approved else "rejected",
        message="Action approved and executed" if request.approved else "Action rejected"
    )

