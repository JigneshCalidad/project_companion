"""Routes package."""

from app.routes.scan import router as scan_router
from app.routes.ask import router as ask_router
from app.routes.action import router as action_router
from app.routes.graph import router as graph_router
from app.routes.settings import router as settings_router

__all__ = ['scan_router', 'ask_router', 'action_router', 'graph_router', 'settings_router']

